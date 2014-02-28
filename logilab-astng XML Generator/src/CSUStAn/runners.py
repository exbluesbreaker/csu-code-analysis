'''
Created on 08.04.2012

@author: bluesbreaker
'''

import imp
import re
import pydot
import os
from lxml import etree
import hashlib

from logilab.common.configuration import ConfigurationMixIn
from logilab.astng.manager import astng_wrapper, ASTNGManager
from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import *

from pylint.pyreverse.diadefslib import DiadefsHandler
from pylint.pyreverse.utils import insert_default_options
from pylint.pyreverse.main import OPTIONS
from pylint.pyreverse import writer, main
from pylint.pyreverse.utils import get_visibility
from CSUStAn.astng.simple import NamesCheckLinker
from CSUStAn.tracing.class_tracer import CSUDbg
from CSUStAn.reflexion.rm_tools import ReflexionModelVisitor,HighLevelModelDotGenerator,SourceModelXMLGenerator
from CSUStAn.astng.inspector import NoInferLinker, ClassIRLinker
from CSUStAn.astng.astng import ASTNGHandler
from CSUStAn.astng.control_flow import CFGLinker,CFGHandler
from CSUStAn.exceptions import CSUStAnException
from logilab.astng.inspector import IdGeneratorMixIn



'''Entry points for different ASTNG processing'''

class ReflexionModelRunner(ConfigurationMixIn):
    """Reflexion model runner"""
    
    def __init__(self, project_name,hm_model,mapper):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        #insert_default_options()
        self.manager = ASTNGManager()
        #self.register_options_provider(self.manager)
        #args = self.load_command_line_configuration()
        #args = args[0:1]
        self.run(project_name,hm_model,mapper)

    def run(self, project_name,hm_model,mapper):
        project = self.manager.project_from_files([project_name], astng_wrapper)
        self.project = project 
        linker = NamesCheckLinker(project, tag=True)
        linker.link_imports(project)
        rm_linker = ReflexionModelVisitor(project,mapper,hm_model)
        rm_linker.compute_rm()
        rm_linker.write_rm_to_png(project_name)
        xml_writer = SourceModelXMLGenerator()
        xml_root = xml_writer.generate(project_name, rm_linker.sm_call_deps,rm_linker.ignored_modules)
        xml_writer.write_to_file(project_name+"_sm.xml")
        dot_writer = HighLevelModelDotGenerator()
        graph = dot_writer.generate(mapper.get_hm_entities(), hm_model)
        graph.write_png(project_name+'_high-level_model.png')
        
        
class ClassIRRunner(ConfigurationMixIn):
    # generate XML, describing classes of project
    
    options = OPTIONS
    
    # criteria for duck typing
    _criteria = None
    _out_file = None
    _project = None
    _good_gettatr = 0
    _bad_gettatr = 0
    # numbers of "ducks" in project (for complexity estimation)
    _all_ducks = 0
    # numbers of classes in project (for complexity estimation)
    _all_classes = 0
    _found_ducks = 0
    _prob_used_classes = None
    _dbg_assattr_parents = None 
    _list_attrs = [attr for attr in dir([]) if not re.search('\A(?!_)',attr)]
    _list_methods = [attr for attr in dir([]) if re.search('\A(?!_)',attr)]
    _dict_attrs = [attr for attr in dir({}) if not re.search('\A(?!_)',attr)]
    _dict_methods = [attr for attr in dir({}) if re.search('\A(?!_)',attr)]
    _tuple_attrs = [attr for attr in dir(()) if not re.search('\A(?!_)',attr)]
    _tuple_methods = [attr for attr in dir(()) if re.search('\A(?!_)',attr)]
    _attr_iteration_cycles = 0
    _treshold = None
    _add_value = None
    
    def __init__(self, args,criteria='default',out_file='test.xml',treshold=None,add_value=False):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        self._add_value = add_value
        self._project = args[0]
        self._treshold = treshold
        self._out_file = out_file
        self._criteria = criteria
        self._prob_used_classes = set([])
        self._dbg_assattr_parents = set([])
        insert_default_options()
        self.manager = ASTNGManager()
        self.register_options_provider(self.manager)
        args = self.load_command_line_configuration()
        self.run(args)
    
    # Check if object is of standard complex type(dict, tuple or list)
    def _check_complex_type(self,attrs,methods):
        if(all(meth in self._list_methods for meth in methods) and
           all(attr in self._list_attrs for attr in attrs)):
            return 'List'
        elif(all(meth in self._dict_methods for meth in methods) and
             all(attr in self._dict_attrs for attr in attrs)):
            return 'Dict'
        elif(all(meth in self._tuple_methods for meth in methods) and
             all(attr in self._tuple_attrs for attr in attrs)):
            return 'Tuple'
        return None


    def check_candidate(self,duck,cand_class, criteria='default'):
        duck_attrs, duck_methods = self.get_duck_signature(duck)
        candidate_attrs = cand_class.cir_complete_attrs
        candidate_methods = set([method.name for method in cand_class.methods()])
        proper_attrs = candidate_attrs.intersection(duck_attrs)
        proper_methods = candidate_methods.intersection(duck_methods)
        value=None
        if criteria == 'default':
            if(all(attr in candidate_attrs for attr in duck_attrs) and all(method in candidate_methods for method in duck_methods)):
                return True
        if criteria == 'capacity':
            value = float(len(proper_attrs)+len(proper_methods))/(len(duck_attrs)+len(duck_methods)) 
        if criteria == 'frequency':
            attr_val = self.get_duck_val(duck, proper_attrs, 'attrs')
            all_attr = self.get_duck_val(duck, duck_attrs, 'attrs')
            meth_val = self.get_duck_val(duck, proper_methods, 'methods')
            all_meth = self.get_duck_val(duck, duck_methods, 'methods')
            value = float(attr_val+meth_val)/(all_attr+all_meth) 
           
        if value is not None:
            if self._add_value:
                if duck.has_key('type_values'):
                    # save value for candidate
                    duck['type_values'][cand_class.cir_uid]=value
                else:
                    duck['type_values']={cand_class.cir_uid:value}
            if value>= self._treshold:
                return True
        return False
    
    def get_duck_signature(self,duck):
        if(duck['complex_type']):
            if duck.has_key('element_signature'):
                # search for class of element is needed
                return set(duck['element_signature']['attrs'].keys()),set(duck['element_signature']['methods'].keys())
        return set(duck['attrs'].keys()), set(duck['methods'].keys())
    
    def get_duck_val(self,duck,names,label):
        if(duck['complex_type']):
            if duck.has_key('element_signature'):
                return sum([duck['element_signature'][label][name] for name in names])
        return sum([duck[label][name] for name in names])

    def run(self, args):
        """checking arguments and run project"""
        if not args:
            print self.help()
            return
        project = self.manager.project_from_files(args, astng_wrapper)
        self.project = project
        linker = ClassIRLinker(project)
        linker.visit(project)
        bad_ducks = 0
        successes = 0
        ducks_num = len(list(linker.get_ducks()))
        count = 1
        dbg = set([])
        empty_ducks = 0
        """ Handle "duck" information and generate information about types """
        for current_class in linker.get_classes():
            for duck in current_class.cir_ducks.keys():
                print "Processing ", count, " duck of ",ducks_num
                count +=1
                duck_attrs, duck_methods = self.get_duck_signature(current_class.cir_ducks[duck])
                # ignore empty ducks
                if((not duck_attrs) and (not duck_methods)):
                    empty_ducks+=1
                    continue
                if not hasattr(current_class.cir_ducks[duck], 'complex_type'):
                    # if duck is not detected  as complex type on previous stage (according to [],{} etc. usage)
                    # we need to check its methods and fields
                    complex_type = self._check_complex_type(duck_attrs, duck_methods)
                    if(complex_type):
                        current_class.cir_ducks[duck]['complex_type'] = complex_type
                        self._found_ducks+=1
                        continue
                duck_found = False
                for field_candidate in linker.get_classes():
                    result = self.check_candidate(current_class.cir_ducks[duck], field_candidate,self._criteria)
                    if(result):
                        current_class.cir_ducks[duck]['type'].append(field_candidate)
                        self._prob_used_classes |= set([field_candidate.cir_uid]) 
                    duck_found = result or duck_found
                      
                #check if duck not found at all
                if(not duck_found):
                    bad_ducks += 1
                else:
                    self._found_ducks+=1 
                    dbg.add(str(current_class)+duck)
#        empty_ducks = len(list(linker.get_empty_ducks()))  
        print len(dbg)
        print "Project - ",self._project        
        print "Duck typing criteria - ",self._criteria            
        print "Numbers of ducks: ", linker.get_ducks_count()
        print "Numbers of ducks with assignment in class: ", len(list(linker.get_assigned_ducks()))
        print "Numbers of ducks with complex type: ", len(list(linker.get_complex_ducks()))
        if(linker.get_ducks_count()!=empty_ducks):
            print "Found ducks: ",self._found_ducks, " percentage from non-empty ducks: ",round(100*float(self._found_ducks)/(linker.get_ducks_count()-empty_ducks),1), " %"
        if(linker.get_attrs_count()!=0):
            print "Numbers of all attributes in project: ", linker.get_attrs_count(), " percentage of found attrs: ",round(100*float(self._found_ducks)/linker.get_attrs_count(),1), " %"
        print "Numbers of classes: ",len(list(linker.get_classes()))
        if(len(list(linker.get_classes()))!=0):
            print "Probably used (as field) classes: ",len(self._prob_used_classes)," percentage: ",round(100*float(len(self._prob_used_classes))/len(list(linker.get_classes())),1), " %"
        
        # result XML generation
        mapper = {}
        root = etree.Element("Classes")
        for obj in linker.get_classes():
            self._all_classes +=1
            node = etree.Element("Class",name=obj.name,fromlineno=str(obj.fromlineno),col_offset=str(obj.col_offset),id=str(obj.cir_uid),label=obj.root().name)
            mapper[obj] = node
            root.append(node)
            for attrname in obj.cir_attrs:
                attr_node = etree.Element('Attr',name=attrname)
                mod_node = etree.Element('Modifier',name=get_visibility(attrname))
                attr_node.append(mod_node)
                node.append(attr_node)
                if(attrname in obj.cir_ducks):
                    if obj.cir_ducks[attrname]['complex_type']:
                        for prob_type in obj.cir_ducks[attrname]['type']:
                            attr_node.append(etree.Element('AggregatedType',name=str(obj.cir_ducks[attrname]['complex_type']),element_type=prob_type.name,element_id=str(prob_type.cir_uid)))
                    else:
                        for prob_type in obj.cir_ducks[attrname]['type']:
                            if(obj.cir_ducks[attrname].has_key('type_values')):
                                common_type_node = etree.Element('CommonType',
                                                                 name=prob_type.name,
                                                                 id=str(prob_type.cir_uid),
                                                                 type_value=str(obj.cir_ducks[attrname]['type_values'][prob_type.cir_uid]))
                            else:
                                common_type_node = etree.Element('CommonType',
                                                                 name=prob_type.name,
                                                                 id=str(prob_type.cir_uid))
                            attr_node.append(common_type_node)    
            for meth in linker.get_methods(obj):
                meth_node = etree.Element('Method',name=meth.name)
                meth_node.set("fromlineno",str(meth.fromlineno))
                meth_node.set("col_offset",str(meth.col_offset))
                mod_node = etree.Element('Modifier',name=get_visibility(meth.name))
                meth_node.append(mod_node)
                """ This is needed for some native libs(pyx) """
                if(meth.args.args == None):
                    continue
                for arg in meth.args.args:
                    # ignore self arg
                    if not arg.name == 'self':
                        meth_node.append(etree.Element('Arg',name=arg.name))
                node.append(meth_node)
        for rel in linker.get_inheritances():
            mapper[rel[0]].append(etree.Element('Parent',name=rel[1].name,id=str(rel[1].cir_uid)))
        print "Writing ", self._out_file
        f = open(self._out_file,'w')
        f.write(etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
        
class ClassIRHandler:
    # Process XML class IR
    _ucr_tree = None
    _classes = None
    _full_name_dict = None
    _id_dict = None
    def __init__(self, ucr_xml):
        self._ucr_tree = etree.parse(ucr_xml)
        self._classes = [node for node in self._ucr_tree.iter("Class")]
        self._full_name_dict = {}
        self._id_dict = {}
        for class_node in self._classes:
            self._full_name_dict[class_node.get("label")+'.'+class_node.get("name")] = class_node
            self._id_dict[class_node.get("id")] = class_node      
    def get_methods(self,node):
        return set([meth.get("name") for meth in node.iter("Method")])
    def handle_attrs(self,node):
        return set([attr.get("name") for attr in node.iter("Attr")])
    def get_attr(self,node, attrname):
        attrs = [attr for attr in node.iter("Attr") if (attr.get("name")==attrname)]
        if(len(attrs)==0):
            return None
        else:
            return attrs[0]
    def get_common_type_values(self,node, attrname, value_dict= None):
        if value_dict is None:
            value_dict = {}
        attr = self.get_attr(node, attrname)
        if attr is not None:
            for type in attr.iter("CommonType"):
                type_name = self._id_dict[type.get("id")].get("label")+'.'+self._id_dict[type.get("id")].get("name")
                if (value_dict.has_key(type_name)):
                    if value_dict[type_name] < type.get("type_value"):
                        # use maximum value in inheritance hierarchy
                        value_dict[type_name] = type.get("type_value")
                else:
                    value_dict[type_name] = type.get("type_value")
        for parent in self.get_parents(node):
            self.get_common_type_values(parent, attrname, value_dict)
        return value_dict
    def get_type(self,type_mark,node, attrname, type_set= None):
        if type_set is None:
            type_set = set([])
        attr = self.get_attr(node, attrname)
        if attr is not None:
            if(type_mark=="AggregatedType"):
                """ Return type of element"""
                type_set |= set([self._id_dict[type.get("element_id")].get("label")+'.'+self._id_dict[type.get("element_id")].get("name") for type in attr.iter(type_mark)])
            else:
                type_set |= set([self._id_dict[type.get("id")].get("label")+'.'+self._id_dict[type.get("id")].get("name") for type in attr.iter(type_mark)])
        for parent in self.get_parents(node):
            self.get_type(type_mark,parent, attrname, type_set)
        return type_set
    def get_parents(self,node):
        return [self._ucr_tree.xpath("//Class[@id="+parent.get("id")+"]")[0] for parent in node.iter("Parent")]
    def get_all_parents(self,node,result=None):
        if(result is None):
            result = set([])
        parents = [self._ucr_tree.xpath("//Class[@id="+parent.get("id")+"]")[0] for parent in node.iter("Parent")]
        result|= set(parents)
        for p in parents:
            result = self.get_all_parents(p, result)
        return result
    def get_class_by_full_name(self,full_name):
        if self._full_name_dict.has_key(full_name):
            return self._full_name_dict[full_name]
        else: 
            print "None get_class_by_full_name", full_name
            return None
    def get_class_by_id(self,class_id):
        if self._id_dict.has_key(class_id):
            return self._id_dict[class_id]
        else: 
            return None
    def get_classes_from_module(self,modname):
        return self._ucr_tree.xpath("//Class[@label=\""+modname+"\"]")
    def get_num_of_classes(self):
        return len(self._classes)

class FieldCandidateFinder(ConfigurationMixIn,ClassIRHandler):
    # scan classes description for candidate for class's field
    
    options = OPTIONS
    _successes = 0
    _fails = 0
    _ucr_tree = None
    _complete_signatures = None
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        ClassIRHandler.__init__(self, args[0])
        _complete_signatures = {}
        self.run(args)
        
    def _compute_signature(self,id,curr_node=None):
        if(curr_node is None):
            curr_node = self._ucr_tree.xpath("//Class[@id="+id+"]")[0]
        self._complete_signatures[id]['Attrs'] |= Set([re.search('[^ :]*',attr.get("name")).group(0) for attr in curr_node.iter("Attr")])
        self._complete_signatures[id]['Methods'] |= self.get_methods(curr_node)
        parents = self.get_parents(curr_node)
        for parent in parents:
            self._compute_signature(id,parent)

    def run(self, args):
        ducks = [node for node in self._ucr_tree.iter("DuckAttr")]
        # prepare data about classes attrs and methods
        status = 0
        classes_num = len(self._classes)
        for node in self._classes:
            status +=1
            print "Complete ",status,"/",classes_num," class signatures"
            # ProbUsed will be true, if this class will be detect as candidate for duck field
            self._complete_signatures[node.get("id")]={'Attrs':Set([]),'Methods':Set([]),'ProbUsed' : False}
            self._compute_signature(node.get("id"))
        status = 0
        found_ducks = 0
        ducks_num = len(ducks)
        for duck in ducks:
            status +=1
            print "Complete ",status,"/",ducks_num," ducks" 
            duck_attrs = [node.get('name') for node in duck.iter("ProbAttr")]
            duck_methods = [node.get('name') for node in duck.iter("ProbMethod")]
            # ignore empty ducks
            if((not duck_attrs) and (not duck_methods)):
                continue
            max_matches = 0
            duck_found = False
            for id in self._complete_signatures.keys():
                if(all(attr in self._complete_signatures[id]['Attrs'] for attr in duck_attrs) and all(method in self._complete_signatures[id]['Methods'] for method in duck_methods)):
                    self._successes += 1
                    if(not duck_found):
                        found_ducks+=1
                        duck_found = True
                    self._complete_signatures[id]['ProbUsed']=True
                num_matches = sum(attr in self._complete_signatures[id]['Attrs'] for attr in duck_attrs)+sum(method in self._complete_signatures[id]['Methods'] for method in duck_methods)
                if(num_matches >  max_matches):
                    max_matches = num_matches
            #print "Max matches - ",max_matches," from ",len(duck_attrs)+len(duck_methods)
        prob_used_classes = 0
        for id in self._complete_signatures.keys():
            if  self._complete_signatures[id]['ProbUsed']== True:
                prob_used_classes+=1
        print "Numbers of ducks: ",len(ducks)
        print "Found ducks: ",found_ducks, " percentage: ",round(100*float(found_ducks)/len(ducks),1), " %"
        print "Numbers of classes: ",len(self._complete_signatures.keys())
        print "Probably used (as field) classes: ",prob_used_classes," percentage: ",round(100*float(prob_used_classes)/len(self._complete_signatures.keys()),1), " %"
        #for class_node in classes:

class ClassHierarchyVisualizer(ConfigurationMixIn,ClassIRHandler):
    # generate dot from XML classes IR
    
    options = OPTIONS
    _out_file = None
    
    def __init__(self, in_file,out_file):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        ClassIRHandler.__init__(self, in_file)
        self._out_file = out_file
        self.run()
    
    def run(self):
        graph = pydot.Dot(graph_type='digraph')
        dot_classes = {} 
        #setup classes
        for node in self._classes:
            class_text = node.get("name")
            attrs = [a for a in node.iter("Attr")]
            if(len(attrs)>0):
                class_text += "|Attrs|"
            for attr in attrs:
                class_text += attr.get("name")+"\l"
            methods = [m for m in node.iter("Method")]
            if(len(methods)>0):
                class_text += "|Methods|"
            for method in methods:
                class_text += method.get("name")+"\l"
            class_node = pydot.Node(node.get("id"),label="{"+class_text+"}",shape='record')
            dot_classes[node.get("id")] = class_node
            graph.add_node(class_node)
        #setup relations
        for node in self._classes:
            parents = [parent for parent in node.iter("Parent")]
            for parent in parents:
                edge = pydot.Edge(dot_classes[node.get("id")], dot_classes[parent.get("id")])
                graph.add_edge(edge)
#        node_dict = {}
#        for node in nodes:
#            dot_node = pydot.Node(node)
#            graph.add_node(dot_node)
#            node_dict[node] = dot_node
#        for source, target in deps:
#            graph.add_edge(pydot.Edge(node_dict[source], node_dict[target]))
        graph.write_svg(self._out_file)
        
class PotentialSiblingsCounter(ConfigurationMixIn,ClassIRHandler):
    # search for probable inheritance mistakes
    
    options = OPTIONS
    _methods = None
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        ClassIRHandler.__init__(self, args[0])
        self._methods = {}
        self.run()
    
    def run(self):
        status = 0
        classes_num = len(self._classes)
        for node in self._classes:
            print "Complete ",status,"/",classes_num," classes"
            # ProbUsed will be true, if this class will be detect as candidate for duck field
            #self._complete_signatures[node.get("id")]={'Attrs':Set([]),'Methods':Set([]),'ProbUsed' : False}
            for method in self.get_methods(node):
                if self._assign_method(node,method):
                    if self._methods.has_key(method):
                        self._methods[method].append(node.get("id"))
                    else:
                        self._methods[method]=[node.get("id")]
            status +=1
        methods_num = len(self._methods.keys())
        status = 0
        count = 0
        for method in self._methods.keys():
            print "Complete ",status,"/",methods_num," method names"
            if(len(self._methods[method])>1):
                print "Method ",method," implemented in classes(id): ",self._methods[method]
                count+=1
            status +=1
        print count," method names of ",methods_num,"unique method names in project pretend to to be passed to common superclass"
                
                
    def _assign_method(self,node,method,main=True):
        if((not main) and (method in self.get_methods(node))):
            return False
        for parent in self.get_parents(node):
            if(not self._assign_method(parent, method, False)):
                return False            
        return True
    
class TypesComparator(ClassIRHandler):
    
    #dictionary with information about types, got from running program
    _dynamic_types_info = None
    _result = None
    _result_file = None
    _project = None
    _preload_dt_info = None
    
    def __init__(self, class_ir_file,project,result_file=None):
        ClassIRHandler.__init__(self, class_ir_file)
        self._project = project
        self._result = {'not_found_common_types':0,'correct_common_types':0,'not_found_aggr_types':0,'correct_aggr_types':0}
        if result_file is not None:
            self._result_file = result_file
            self.preload_results()
        
    def compare_type_info(self,threshold=None):
        #Save result
        self.save_result()
        self._result = {'not_found_common_types':0,'correct_common_types':0,'not_found_aggr_types':0,'correct_aggr_types':0}
        for current_class in self._dynamic_types_info.keys():
            node = self.get_class_by_full_name(current_class)
            if node is None:
                    continue
            for attrname in self._dynamic_types_info[current_class][1].keys():
                common_type = self.get_type("CommonType",node,attrname)
                aggr_type = self.get_type("AggregatedType",node,attrname)
                for type in self._dynamic_types_info[current_class][1][attrname]['common_type']:
                    common_type_vals = self.get_common_type_values(node, attrname)
                    if type in common_type:
                        type_val = common_type_vals[type]
                        if((threshold is not None) and (type_val is not None)):
                            type_val = float(type_val)
                            if type_val >= threshold:
                                self._result['correct_common_types']+=1
                            else:
                                self._result['not_found_common_types']+=1
                        else:
                            #threshold will not be used
                            self._result['correct_common_types']+=1
                    else:
                        self._result['not_found_common_types']+=1
                for type in self._dynamic_types_info[current_class][1][attrname]['aggregated_type']:
                    if type in aggr_type:
                        self._result['correct_aggr_types']+=1
                    else:
                        self._result['not_found_aggr_types']+=1
    def save_result(self):
        if(self._result_file is not None):
            if(os.path.exists(self._result_file)):
                parser = etree.XMLParser(remove_blank_text=True)
                tree = etree.parse(self._result_file, parser)
                projects = [node for node in tree.getroot().iter("Project") if node.get("name")==self._project]
                for project in projects:
                    tree.getroot().remove(project)
                project = etree.Element("Project",name=self._project)
                tree.getroot().append(project)
                tree = tree.getroot()
            else:
                tree = etree.Element("DynamicResults")
                project = etree.Element("Project",name=self._project)
                tree.append(project)
            for c in self._dynamic_types_info.keys():
                c_node = etree.Element("Class",name=c)
                project.append(c_node)
                for attr in self._dynamic_types_info[c][1].keys():
                    a_node = etree.Element("Attr",name=attr)
                    c_node.append(a_node)
                    for ct in self._dynamic_types_info[c][1][attr]['common_type']:
                        ct_node = etree.Element("CommonType",name=ct)
                        a_node.append(ct_node)
                    for at in self._dynamic_types_info[c][1][attr]['aggregated_type']:
                        at_node = etree.Element("AggregatedType",name=at)
                        a_node.append(at_node)
            f = open(self._result_file,'w')
            f.write(etree.tostring(tree, pretty_print=True, encoding='utf-8', xml_declaration=True))
            f.close()
    def preload_results(self):
        if(not os.path.exists(self._result_file)):
            self._preload_dt_info = {}
            return
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(self._result_file, parser)
        projects = [node for node in tree.getroot().iter("Project") if node.get("name")==self._project]
        if(projects is None):
            self._preload_dt_info = {}
            return
        dt_info = {}
        for project in projects:
            for c in project.iter("Class"):
                if not dt_info.has_key(c.get("name")):
                    dt_info[c.get("name")] = [0, {}]
                for attr in c.iter("Attr"):
                    if not dt_info[c.get("name")][1].has_key(attr.get("name")):
                        dt_info[c.get("name")][1][attr.get("name")]={'common_type':set([]),'aggregated_type':set([])}
                    for ct in attr.iter("CommonType"):
                        dt_info[c.get("name")][1][attr.get("name")]['common_type'].add(ct.get("name"))
                    for at in attr.iter("AggregatedType"):
                        dt_info[c.get("name")][1][attr.get("name")]['aggregated_type'].add(at.get("name")) 
        self._preload_dt_info = dt_info
             
            
    def get_result(self):
        return self._result.copy()
    

class ObjectTracer(TypesComparator):
    def __init__(self, project_tag, in_file, preload_file, skip_classes=(), delay=5,only_preload=False):
        TypesComparator.__init__(self, in_file,project_tag,preload_file)
        self._dbg = CSUDbg(project_mark=project_tag, skip_classes=skip_classes, delay=delay,preload_dt_info=self._preload_dt_info)
        self._dbg.set_trace()
        curr_dir = os.getcwd()
        if not only_preload:
            try:
                self.run()
            except SystemExit:
                """ Catching sys.exit """
                pass
        os.chdir(curr_dir)
        self._dbg.disable_trace()
        used_classes = self._dbg.get_used_classes()
        self._dynamic_types_info = used_classes
        t=0.1
        while t <=1.0:
            self.compare_type_info(threshold=t)
            print len(self._dynamic_types_info.keys()), self.get_num_of_classes()
            res =  self.get_result()
            print "Threshold - ", t
            print "Correctly detected common types: ",res['correct_common_types']
            print "Correctly detected aggregated types: ",res['correct_aggr_types']
            print "Not correctly detected common types: ",res['not_found_common_types']
            print "Not correctly detected aggregated types: ",res['not_found_aggr_types']
            print "Success percentage: ",(res['correct_common_types']+res['correct_aggr_types'])*100.0/(res['correct_common_types']+res['correct_aggr_types']+res['not_found_common_types']+res['not_found_aggr_types']),"%"
            t += 0.05
                        

class LogilabObjectTracer(ObjectTracer):
    
    def __init__(self, in_file, preload_file,only_preload=False):
        ObjectTracer.__init__(self,'logilab', in_file ,preload_file,skip_classes=(Const),only_preload=True)
        
    def run(self):
        main.Run(sys.argv[1:])

class TwistedObjectTracer(ObjectTracer):
    
    def __init__(self, in_file,preload_file):
        ObjectTracer.__init__(self,'twisted', in_file ,preload_file)
        
    def run(self):
        twisted_ftpclient.run()
        
class PylintObjectTracer(ObjectTracer):
    
    def __init__(self, in_file, preload_file,only_preload=False):
        ObjectTracer.__init__(self,'pylint', in_file ,preload_file,skip_classes=(Const),only_preload=only_preload)
        
    def run(self):
        from pylint import lint
        lint.Run(sys.argv[1:])
     
class SconsObjectTracer(ObjectTracer):
    
    def __init__(self, in_file, preload_file):
        from SCons.Script.SConsOptions import SConsValues
        from SCons.Builder import CompositeBuilder
        from SCons.Node.FS import File
        from SCons.Builder import BuilderBase
        from SCons.Script.SConscript import SConsEnvironment
        ObjectTracer.__init__(self,'SCons', in_file ,preload_file,skip_classes=(SConsValues,CompositeBuilder,File,BuilderBase,SConsEnvironment),delay=1)
        
    def run(self):
        foo = imp.load_source('scons','/usr/bin/scons')
        os.chdir('/home/bluesbreaker/Development/ascend-0.9.8')
        import scons
        import SCons.Script
        # this does all the work, and calls sys.exit
        # with the proper exit status when done.
        SCons.Script.main()

class BazaarObjectTracer(ObjectTracer):
    
    _work_dir = None
    
    def __init__(self, in_file, preload_file,work_dir,only_preload=False):
        import sys
        sys.setrecursionlimit(10000)
        from bzrlib.lazy_regex import LazyRegex
        self._work_dir = work_dir
        ObjectTracer.__init__(self,'bzrlib', in_file ,preload_file, skip_classes=(LazyRegex), delay=20,only_preload=only_preload)
        
    def run(self):
        os.chdir(self._work_dir)
        import bzrlib
        library_state = bzrlib.initialize()
        library_state.__enter__()
        try:
            exit_val = bzrlib.commands.main()
        finally:
            library_state.__exit__(None, None, None)

        
class TestRunner(ConfigurationMixIn):
    options = OPTIONS
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        insert_default_options()
        self.manager = ASTNGManager()
        self.register_options_provider(self.manager)
        args = self.load_command_line_configuration()
        self.run(args)
        
    def run(self,args):
        project = self.manager.project_from_files(args, astng_wrapper)
        self.project = project
        linker = ClassIRLinker(project)
        linker.visit(project)

class CFGExtractor(ASTNGHandler):
    _project_name = None
    _out_xml = None
    def __init__(self,project,out_xml):
        self._project_name = project
        self._out_xml = out_xml
        ASTNGHandler.__init__(self,[project])
        self.run()
    def run(self):
        linker = CFGLinker(self._project_name,self._out_xml)
        linker.visit(self.project)
        
class DataflowLinker(CFGHandler,ClassIRHandler):
    _targeted = 0
    _out_xml = None
    _typed_ga_calls = 0
    _unknown_ga_calls = 0
    _class_dict = {}
    def __init__(self,ucr_xml,cfg_xml,out_xml):
        ClassIRHandler.__init__(self, ucr_xml)
        CFGHandler.__init__(self, cfg_xml)
        self._out_xml = out_xml
        self.run()
    def run(self):
        self.link_methods(self._cfg_tree)
    def link_methods(self,xml_node):
        for meth in self._cfg_tree.xpath("//Method"):
            parent_class = self.get_class_by_full_name(meth.get("label")+'.'+meth.get("parent_class"))
            meth.set("ucr_id",parent_class.get("id"))
            self._class_dict[parent_class.get("id")+meth.get("name")]=meth
        for call in self._cfg_tree.xpath("//TargetClass"):
            target_class = self.get_class_by_full_name(call.get("label")+'.'+call.getparent().getparent().get("name"))
            if(not target_class is None):
                call.set("ucr_id",target_class.get("id"))
        for call in self._cfg_tree.xpath("//Getattr[starts-with(@label,\"self.\")]"):
            frame = call.getparent().getparent().getparent()
            if(frame.tag=='Method'):
                source_class = self.get_class_by_full_name(frame.get("label")+'.'+frame.get("parent_class"))
                attr = self.get_attr(source_class,call.get("label")[5:])
                if(attr is not None):
                    attr_types = list(attr.iter("CommonType"))
                    if(len(attr_types)>0):
                        self._typed_ga_calls +=1
                    else:
                        self._unknown_ga_calls +=1
                        target_node = etree.Element("Target",type="unknown")
                        call.append(target_node)
                    for t in attr_types:
                        if self._class_dict.has_key(t.get("id")+call.get("name")):
                            meth = self._class_dict[t.get("id")+call.get("name")]
                            tgt_node = etree.Element("Target",type="method", cfg_id=meth.get("cfg_id"))
                            call.append(tgt_node)
                        else:
                            tgt_node = etree.Element("Target",type="method")
                            call.append(tgt_node)
                        tgt_class_node = etree.Element("TargetClass", ucr_id=t.get("id"))
                        tgt_node.append(tgt_class_node)
        f = open(self._out_xml,'w')
        f.write(etree.tostring(self._cfg_tree, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
        print "Found ",self._targeted," UCR classes"
        print "Found getattr calls ",self._typed_ga_calls,"  unknown - ", self._unknown_ga_calls
        
class CFGVisualizer(CFGHandler):
    _out_dir = None
    def __init__(self,lcfg_xml,out_dir):
        CFGHandler.__init__(self, lcfg_xml)
        self._out_dir = out_dir
        self.run()
    def run(self):
        for meth in self._cfg_tree.xpath("//Method"):
            self.handle_frame(meth)
        for func in self._cfg_tree.xpath("//Function"):
            self.handle_frame(func)
    def handle_frame(self,node):
        graph = pydot.Dot(graph_type='digraph',compound='true')
        block_dict = {}
        call_cnt = 0
        for block in node.iter("Block"):
            block_node = pydot.Cluster(block.get("id")+'_',shape='record',label='Block '+str(block.get("id")))
            dbg_cnt = call_cnt
            call_node = None
            for c in block.iter("Call"):
                call_color = 'black'
                call_url = '#'
                if((len(c.getchildren())>0) and (c.getchildren()[0].get("called")=='class')):
                    call_color = 'blue'
                elif((len(c.getchildren())>0) and (c.getchildren()[0].get("called")=='function')):
                    call_color = 'yellow'
                elif((len(c.getchildren())>0) and (c.getchildren()[0].tag=='Getattr')):
                    call_color = 'green'
                if (((len(c.getchildren())>0)) and('called_id'in c.getchildren()[0].keys())):
                    call_url = os.path.abspath(self._out_dir+'/'+c.getchildren()[0].get('called_id')+'.svg')
                    call_color = 'red'
                call_node = pydot.Node('Call '+str(dbg_cnt),shape='record',color=call_color,URL=call_url)
                dbg_cnt += 1
                block_node.add_node(call_node)
            if dbg_cnt == call_cnt:
                block_node = pydot.Node('Block '+str(block.get("id")),shape='record')
                graph.add_node(block_node)
                block_dict[block.get("id")] = block_node
            else:
                graph.add_subgraph(block_node)
                block_dict[block.get("id")] = (block_node,call_node)
                call_cnt = dbg_cnt
        for block in node.iter("If"):
            block_node = pydot.Node('If '+block.get("id"),shape='diamond')
            #block.get("test")
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for block in node.iter("For"):
            block_node = pydot.Node('For '+block.get("id"),shape='diamond')
            #block.get("iterate")
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for block in node.iter("While"):
            block_node = pydot.Node('While '+block.get("id"),shape='diamond')
            #block.get("test")
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for block in node.iter("TryExcept"):
            block_node = pydot.Node('TryExcept',shape='diamond')
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for block in node.iter("TryFinally"):
            block_node = pydot.Node('TryFinally',shape='diamond')
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for block in node.iter("With"):
            block_node = pydot.Node('With',shape='diamond')
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for flow in node.iter("Flow"):
            from_node = block_dict[flow.get("from_id")]
            if isinstance(from_node,tuple):
                tail = from_node[1]
                tail_l = from_node[0]
            else:
                tail=from_node
                tail_l = None
            to_node = block_dict[flow.get("to_id")]
            if isinstance(to_node,tuple):
                head = to_node[1]
                head_l = to_node[0]
            else:
                head = to_node
                head_l = None
            if((tail_l is None) and (head_l is None)):
                dot_edge = pydot.Edge(tail,head)
            elif((tail_l is not None) and (head_l is None)):
                dot_edge = pydot.Edge(tail,head,ltail=tail_l.get_name())
            elif((tail_l is None) and (head_l is not None)):
                dot_edge = pydot.Edge(tail,head,lhead=head_l.get_name())
            else:
                dot_edge = pydot.Edge(tail,head,ltail=tail_l.get_name(),lhead=head_l.get_name())
            graph.add_edge(dot_edge)
        graph.write_svg(self._out_dir+'/'+node.get("cfg_id")+'.svg')

class UCRSlicer(ClassIRHandler):
    # search for probable inheritance mistakes
    _sliced_classes = set([])
    _out_file = None
    
    def __init__(self, in_file,out_file):
        ClassIRHandler.__init__(self, in_file)
        self._out_file = out_file
        
        
    def run(self):
        self.slice()
        self.extract_slicing()
        
    def extract_slicing(self):
        root_node = etree.Element("Classes")
        for c in self._sliced_classes:
            root_node.append(c)
        f = open(self._out_file,'w')
        f.write(etree.tostring(root_node, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
                

class InheritanceSlicer(ConfigurationMixIn,UCRSlicer):
    # search for probable inheritance mistakes
    
    options = OPTIONS
    _methods = None
    _class_id = None
    
    def __init__(self, in_file,out_file, class_id):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        UCRSlicer.__init__(self, in_file,out_file)
        self._methods = {}
        self._class_id = class_id
        self.run()
        
    def slice(self):
        self.slice_class(self._id_dict[self._class_id])
        
    def slice_class(self,node):
        self._sliced_classes.add(node)
        for p in self.get_parents(node):
            self.slice_class(p)
            
class CFGSlicer(CFGHandler):
    _out_xml = None
    _sliced_frames = None
    
    def __init__(self,lcfg_xml,out_xml):
        CFGHandler.__init__(self, lcfg_xml)
        self._out_xml = out_xml
        
    
    def slice(self):
        self.extract_slicing()
        ''' Extract sliced methods/funcs from CFG'''
        for frame in self._cfg_tree.xpath("//Method|//Function"):
            if frame not in self._sliced_frames:
                frame.getparent().remove(frame)
        f = open(self._out_xml,'w')
        f.write(etree.tostring(self._cfg_tree, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
            
class FlatCFGSlicer(CFGSlicer):
    _id = None
    _criteria = None
    
    def __init__(self,lcfg_xml,out_xml,target_id,criteria):
        CFGSlicer.__init__(self, lcfg_xml,out_xml)
        self._id = target_id
        self._criteria = criteria
        self.slice()
        
    def extract_slicing(self):
        if self._criteria == "callers":
            self.handle_callers()
        elif self._criteria == "tree":
            self.handle_tree()
        else:
            print "Unknown CFG slicing criteria!"
            return
        print len(self._sliced_frames),"methods after slicing"
    
    def handle_tree(self,node_id=None):
        ''' Slice methods/funcs called from given'''
        if node_id is None:
            self._sliced_frames = set([])
            node_id = self._id
        self._sliced_frames|=set(self._cfg_tree.xpath("//Function[@cfg_id=\""+node_id+"\"]|//Method[@cfg_id=\""+node_id+"\"]"))
        calls = self._cfg_tree.xpath("//Method[@cfg_id=\""+node_id+"\"]//Target[@cfg_id]|\
                                                        //Function[@cfg_id=\""+node_id+"\"]//Target[@cfg_id]")
        for id in set([c.get("cfg_id") for c in calls]):
            self.handle_tree(id)
            
    def handle_callers(self):
        ''' Slice callers methods/funcs for given'''
        ''' method/func of interest'''
        self._sliced_frames=set(self._cfg_tree.xpath("//Function[@cfg_id=\""+self._id+"\"]|//Method[@cfg_id=\""+self._id+"\"]"))
        ''' calls of method/func of interest'''
        for call in self._cfg_tree.xpath("//Target[@cfg_id=\""+self._id+"\"]"):
            self._sliced_frames.add(call.getparent().getparent().getparent().getparent())
            
class ClassCFGSlicer(CFGSlicer):
    _ucr_id = None
    _criteria = None  
    
    def __init__(self, lcfg_xml, out_xml, target_id, criteria):
        CFGSlicer.__init__(self, lcfg_xml, out_xml)
        self._ucr_id = target_id
        self._criteria = criteria
        self.slice()
    
    def extract_slicing(self):
        if self._criteria == "creators":
            self.handle_creators()
        elif self._criteria == "created":
            self.handle_created()
        else:
            print "Unknown CFG slicing criteria!"
            return
        print len(self._sliced_frames), "methods after slicing"
        
        
    def handle_creators(self):
        ''' Slice method/funcs,which created given class'''
        self._sliced_frames = set([])
        ''' calls of method/func of interest'''
        for call in self._cfg_tree.xpath("//TargetClass[@ucr_id=\"" + self._ucr_id + "\"]"):
            if call.getparent().getparent().tag=='Direct':
                self._sliced_frames.add(call.getparent().getparent().getparent().getparent().getparent())
                

class ExecPathHandler(CFGHandler,IdGeneratorMixIn):
    
    def __init__(self,lcfg_xml):
        CFGHandler.__init__(self, lcfg_xml)
        IdGeneratorMixIn.__init__(self)
    
    def get_call_route(self,block_path,call):
        call_path=[]
        for b in block_path[:-1]:
            for c in b.iter("Call"):
                call_path.append(c)
        for c in block_path[-1].iter("Call"):
            call_path.append(c)
            if(c.xpath(".//Target[@cfg_id=\""+call+"\"]")):
                break
        return call_path
            
    def extract_frame_path(self,frame_node,block_node):
        ''' Extract all possible paths from frame start to given block '''
        flows = frame_node.xpath(".//Flow[@to_id=\'"+block_node.get("id")+"\']")
        # local_path |= set(flows)
        local_path = []
        if len(flows)==0:
            return[[block_node]]
        for f in flows:
            precending = frame_node.xpath(".//*[@id=\'"+f.get("from_id")+"\']")
            paths = self.extract_frame_path(frame_node, precending[0])
            #print paths
            for p in paths:
                p.append(block_node)
            local_path = local_path+paths
        return local_path
    
    def extract_frame_routes(self,exec_path):
        '''Extract all possible global frame routes for given path'''
        curr_frame_calls = self.get_call_targets(exec_path[0])
        frame = self.get_frame_by_id(exec_path[0])[0]
        frame_routes = []
        frame_names = [frame.get("label")+'.'+frame.get("name")]
        for f in exec_path[1:]:
            target_calls=[c for c in curr_frame_calls if c.get("cfg_id")==f]
            if len(target_calls)==0:
                raise CSUStAnException("No such exec path"+str(exec_path)+". Failed on "+str(f))
            for c in target_calls:
                block = c.xpath("./ancestor::Block")[0]
                frame_routes.append(self.extract_frame_path(frame, block)) 
            curr_frame_calls = self.get_call_targets(f)
            frame = self.get_frame_by_id(f)[0]
            frame_names.append(frame.get("label")+'.'+frame.get("name"))  
        return frame_names, frame_routes      
    
    def get_call_targets(self,frame_id):
        nodes =  self.get_frame_by_id(frame_id)
        if(len(nodes)>1):
            print "Warning: multiple nodes for exec path entry id(",frame_id,")"
        if(len(nodes)==0):
            raise CSUStAnException("Error: No nodes for exec path entry id("+str(frame_id)+")")
            return None
        return nodes[0].xpath(".//Target[@cfg_id]")

class ExecRouteVisualizer(ExecPathHandler,IdGeneratorMixIn):
    ''' Class for visualization of one exec route '''
    def __init__(self,lcfg_xml):
        ExecPathHandler.__init__(self, lcfg_xml)
        IdGeneratorMixIn.__init__(self)
    
    def dot_route(self,route,exec_path,frame_names):
        graph = pydot.Dot(graph_type='digraph',compound='true')
        prev = None
        for r,f,f_name in zip(route,exec_path[:-1],frame_names[:-1]):
            func_node = pydot.Cluster(str(self.generate_id()),shape='record',label=f_name+"(cfg_id="+f+")")
            blocks = []
            for b in r:
                block_node = self.dot_block(b)
                if isinstance(block_node, tuple):
                    func_node.add_subgraph(block_node[0])
                    blocks.append(block_node)
                else:
                    func_node.add_node(block_node)
                    blocks.append(block_node)
            route_edges = zip(blocks[:-1],blocks[1:])
            if prev is not None:
                route_edges.append((prev,blocks[0]))
            for from_node,to_node in route_edges:
                dot_edge = self.dot_flow_edge(from_node,to_node)
                graph.add_edge(dot_edge)
            graph.add_subgraph(func_node)
            prev = blocks[-1]
        last_func = pydot.Cluster(str(self.generate_id()),shape='record',label=frame_names[-1])
        graph.add_subgraph(last_func)
        last_node = pydot.Node(str(self.generate_id()),shape='record',label='Func '+exec_path[-1])
        dot_edge = pydot.Edge(prev[1],last_node,ltail=prev[0].get_name(),lhead=last_func.get_name())
        last_func.add_node(last_node)
        graph.add_edge(dot_edge)
        return graph
    
    def concat_routes(self,start_routes,end_routes):
        result = []
        for r0 in start_routes:
            for r1 in end_routes:
                r0.append(r1)
                result.append(r0)
        return result
    
    def dot_call(self,call_node):
        dot_id = self.generate_id()
        target = call_node.getchildren()[0]
        cfg_targets = call_node.xpath(".//Target[@cfg_id]")
        if len(cfg_targets)>0:
            cfg_target = "(cfg_id="+cfg_targets[0].get("cfg_id")+")"
        else:
            cfg_target = ""
        if(target.tag == "Getattr"):
            dot_call = pydot.Node(str(dot_id), label="\""+target.get("label") + '.' + target.get("name")+cfg_target+"\"", shape='record')
        else:
            dot_call = pydot.Node(str(dot_id), label="\""+target.get("name")+cfg_target+"\"", shape='record')
        return dot_call
    
    def dot_block(self,block):
        dot_id = self.generate_id()
        cond_blocks = ["If","While","For","With","TryExcept","TryFinally"]
        if block.tag in cond_blocks:
            block_node = pydot.Node(dot_id,label=block.tag,shape='diamond')
            return block_node
        call_nodes = [c for c in block.iter("Call")]
        if(len(call_nodes)>0):
            block_node = pydot.Cluster(str(dot_id),shape='record',label='Block '+str(block.get("id")))
            for c in call_nodes[:-1]:
                call_node = self.dot_call(c)
                block_node.add_node(call_node)
            call_node = self.dot_call(call_nodes[-1])
            block_node.add_node(call_node)
            return block_node,call_node
        else:
            block_node = pydot.Node(str(dot_id),shape='record',label='Block '+str(block.get("id")))
            return block_node
    
    def dot_flow_edge(self,from_node,to_node):
        if isinstance(from_node,tuple):
            tail = from_node[1]
            tail_l = from_node[0]
        else:
            tail=from_node
            tail_l = None
        if isinstance(to_node,tuple):
            head = to_node[1]
            head_l = to_node[0]
        else:
            head = to_node
            head_l = None
        if((tail_l is None) and (head_l is None)):
            dot_edge = pydot.Edge(tail,head)
        elif((tail_l is not None) and (head_l is None)):
            dot_edge = pydot.Edge(tail,head,ltail=tail_l.get_name())
        elif((tail_l is None) and (head_l is not None)):
            dot_edge = pydot.Edge(tail,head,lhead=head_l.get_name())
        else:
            dot_edge = pydot.Edge(tail,head,ltail=tail_l.get_name(),lhead=head_l.get_name())
        return dot_edge
    
class ExecPathVisualizer(ExecRouteVisualizer):
    ''' Visualizer for all routes of given exec path, also fuctions from CFG will be visualized '''
       
    def __init__(self,lcfg_xml,exec_path,out_dir='.'):
        ExecRouteVisualizer.__init__(self, lcfg_xml)
        self._out_dir = out_dir   
        self.visualize_frames(exec_path)
        self.visualize_exec_path(exec_path)
        
    def visualize_exec_path(self,exec_path):
        '''Visualize all possible routes for given exec path '''
        frame_names, frame_routes = self.extract_frame_routes(exec_path)
        result_routes = [[f] for  f in frame_routes[0]]
        i=0
        for r in frame_routes[1:]:
            result_routes = self.concat_routes(result_routes, r)
        for route in result_routes:
            graph = self.dot_route(route,exec_path,frame_names)
            graph.write(self._out_dir+'/route'+str(i)+'.dot')
            graph.write_svg(self._out_dir+'/route'+str(i)+'.svg')
            i+=1
        
    def visualize_frames(self,exec_path):
        frames = [self.get_frame_by_id(f)[0] for f in exec_path]
        graph = pydot.Dot(graph_type='digraph',compound='true')
        for f in frames:
            frame_graph = pydot.Cluster(f.get("cfg_id"),shape='record',label=f.get("label")+'.'+f.get("name")+"(cfg_id="+f.get("cfg_id")+")")
            block_dict = {}
            for block in f.iter("Block"):
                block_node = self.dot_block(block)
                if isinstance(block_node, tuple):
                    frame_graph.add_subgraph(block_node[0])
                    block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
                else:
                    frame_graph.add_node(block_node)
                    block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("If"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("For"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("While"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("TryExcept"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("TryFinally"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("With"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for flow in f.iter("Flow"):
                from_node = block_dict[flow.get("from_id")+'_'+f.get("cfg_id")]
                to_node = block_dict[flow.get("to_id")+'_'+f.get("cfg_id")]
                dot_edge = self.dot_flow_edge(from_node, to_node)
                frame_graph.add_edge(dot_edge)
            graph.add_subgraph(frame_graph)
        graph.write(self._out_dir+'/frames.dot')
        graph.write_svg(self._out_dir+'/frames.svg')
        
class ExecPathObjectSlicer(ExecRouteVisualizer):
    def __init__(self,lcfg_xml,exec_path,out_dir='.'):
        ExecRouteVisualizer.__init__(self, lcfg_xml)
        frame_names, routes  = self.extract_frame_routes(exec_path)
        self.run(routes)
        
    def run(self,routes):
        for r in routes:
            print len(r)
            for f in r:
                print f
                
class InstanceInitSlicer(CFGHandler, UCRSlicer):
    _ucr_id = None
    _keep_parents = None
    def __init__(self,ucr_xml,lcfg_xml,ucr_id,out_xml,keep_parents=False):
        UCRSlicer.__init__(self, ucr_xml,out_xml)
        CFGHandler.__init__(self, lcfg_xml)
        self._ucr_id = ucr_id
        self._keep_parents = keep_parents
        self.run()
        
        
    def slice(self):
        current_class = self.get_class_by_id(self._ucr_id)
        self._sliced_classes.add(current_class)
        parents = None
        if(self._keep_parents):
                parents = self.get_all_parents(current_class,parents)
        else:
            for p in current_class.iter("Parent"):
                    current_class.remove(p)
        for c in self._cfg_tree.xpath("//Method[@ucr_id=\""+self._ucr_id+"\"]//Direct//Target[@type=\"method\"]//TargetClass[@ucr_id]"):
            created_class = self.get_class_by_id(c.get("ucr_id"))
            self._sliced_classes.add(created_class)
            if(self._keep_parents):
                parents = self.get_all_parents(created_class,parents)
            else:
                for p in created_class.iter("Parent"):
                    created_class.remove(p)
        if parents is not None:
            for p in parents:
                self._sliced_classes.add(p)
    
