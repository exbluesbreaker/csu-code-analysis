'''
Created on 08.04.2012

@author: bluesbreaker
'''

import imp
import re
import pydot
import os
from lxml import etree
from twisted.internet import reactor

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
from CSUStAn.tests import twisted_ftpclient, twisted_getpage, twisted_ptyserv, twisted_testlogging
from CSUStAn.astng.inspector import NoInferLinker, ClassIRLinker
from CSUStAn.astng.astng import ASTNGHandler
from CSUStAn.astng.control_flow import CFGLinker



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
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
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
        """ Handle "duck" information and generate information about types """
        for current_class in linker.get_classes():
            for duck in current_class.cir_ducks.keys():
                print "Processing ", count, " duck of ",ducks_num
                count +=1
                if(current_class.cir_ducks[duck]['complex_type']):
                    #self._found_ducks+=1
                    # duck is complex type, nothing to do with it
                    # TODO recursively complex types
                    if current_class.cir_ducks[duck].has_key('element_signature'):
                        # search for class of element is needed 
                        duck_attrs = current_class.cir_ducks[duck]['element_signature']['attrs']
                        duck_methods = current_class.cir_ducks[duck]['element_signature']['methods']
                    else:
                        # duck of complex type and no duck info about element
                        continue
                else:
                    duck_attrs = current_class.cir_ducks[duck]['attrs']
                    duck_methods = current_class.cir_ducks[duck]['methods']
                # ignore empty ducks
                if((not duck_attrs) and (not duck_methods)):
                    continue
                duck_found = False
                for field_candidate in linker.get_classes():
                    complex_type = self._check_complex_type(duck_attrs, duck_methods)
                    if(complex_type):
                        #DEBUG
                        if(current_class.cir_ducks[duck]['complex_type']):
                            if((current_class.cir_ducks[duck]['complex_type'] != complex_type) 
                               and (current_class.cir_ducks[duck]['complex_type'] !='Unknown')):
                                print current_class.cir_ducks[duck]['complex_type'], complex_type
                        #END DEBUG
                        current_class.cir_ducks[duck]['complex_type'] = complex_type
                        if(not duck_found):
                            self._found_ducks+=1
                            duck_found = True
                    candidate_attrs = field_candidate.cir_complete_attrs
                    candidate_methods = set([method.name for method in field_candidate.methods()])
                    if(all(attr in candidate_attrs for attr in duck_attrs) and all(method in candidate_methods for method in duck_methods)):
                        current_class.cir_ducks[duck]['type'].append(field_candidate)
                        successes += 1
                        self._prob_used_classes |= set([field_candidate.cir_uid])
                        if(not duck_found):
                            self._found_ducks+=1
                            duck_found = True
                #check if duck not found at all
                if(not duck_found):
                    bad_ducks += 1
                    print "Bad duck - ",duck_attrs, duck_methods  
        empty_ducks = len(list(linker.get_empty_ducks()))   
        print "Bad ducks ", bad_ducks
        print "Empty ducks ", empty_ducks                   
        print "Numbers of ducks: ", linker.get_ducks_count()
        print "Numbers of ducks with assignment in class: ", len(list(linker.get_assigned_ducks()))
        print "Numbers of ducks with complex type: ", len(list(linker.get_complex_ducks()))
        print "Found ducks: ",self._found_ducks, " percentage from non-empty ducks: ",round(100*float(self._found_ducks)/(linker.get_ducks_count()-empty_ducks),1), " %"
        print "Numbers of all attributes in project: ", linker.get_attrs_count(), " percentage of found attrs: ",round(100*float(self._found_ducks)/linker.get_attrs_count(),1), " %"
        print "Numbers of classes: ",len(list(linker.get_classes()))
        print "Probably used (as field) classes: ",len(self._prob_used_classes)," percentage: ",round(100*float(len(self._prob_used_classes))/len(list(linker.get_classes())),1), " %"
        
        # result XML generation
        mapper = {}
        root = etree.Element("Classes")
        for obj in linker.get_classes():
            self._all_classes +=1
            node = etree.Element("Class",name=obj.name,id=str(obj.cir_uid),label=obj.root().name)
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
                            attr_node.append(etree.Element('CommonType',name=prob_type.name,id=str(prob_type.cir_uid)))       
            for meth in linker.get_methods(obj):
                meth_node = etree.Element('Method',name=meth.name)
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
        f = open('test.xml','w')
        f.write(etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
        
class ClassIRHandler:
    # Process XML class IR
    _tree = None
    _classes = None
    _full_name_dict = None
    _id_dict = None
    def __init__(self, args):
        if(len(args)!=1):
            print "usage <> <file name>"
            exit(0)
        self._tree = etree.parse(args[0])
        self._classes = [node for node in self._tree.iter("Class")]
        self._full_name_dict = {}
        self._id_dict = {}
        for class_node in self._classes:
            self._full_name_dict[class_node.get("label")+'.'+class_node.get("name")] = class_node
            self._id_dict[class_node.get("id")] = class_node      
    def get_methods(self,node):
        return Set([meth.get("name") for meth in node.iter("Method")])
    def handle_attrs(self,node):
        return Set([attr.get("name") for attr in node.iter("Attr")])
    def get_attr(self,node, attrname):
        attrs = [attr for attr in node.iter("Attr") if (attr.get("name")==attrname)]
        if(len(attrs)==0):
            return None
        else:
            return attrs[0]
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
        return [self._tree.xpath("//Class[@id="+parent.get("id")+"]")[0] for parent in node.iter("Parent")]
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
    def get_num_of_classes(self):
        return len(self._classes)

class FieldCandidateFinder(ConfigurationMixIn,ClassIRHandler):
    # scan classes description for candidate for class's field
    
    options = OPTIONS
    _successes = 0
    _fails = 0
    _tree = None
    _complete_signatures = None
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        ClassIRHandler.__init__(self, args)
        _complete_signatures = {}
        self.run(args)
        
    def _compute_signature(self,id,curr_node=None):
        if(curr_node is None):
            curr_node = self._tree.xpath("//Class[@id="+id+"]")[0]
        self._complete_signatures[id]['Attrs'] |= Set([re.search('[^ :]*',attr.get("name")).group(0) for attr in curr_node.iter("Attr")])
        self._complete_signatures[id]['Methods'] |= self.get_methods(curr_node)
        parents = self.get_parents(curr_node)
        for parent in parents:
            self._compute_signature(id,parent)

    def run(self, args):
        ducks = [node for node in self._tree.iter("DuckAttr")]
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
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        ClassIRHandler.__init__(self, args)
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
        graph.write_svg('classes.svg')
        
class PotentialSiblingsCounter(ConfigurationMixIn,ClassIRHandler):
    # search for probable inheritance mistakes
    
    options = OPTIONS
    _methods = None
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        ClassIRHandler.__init__(self, args)
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
        ClassIRHandler.__init__(self, [class_ir_file])
        self._project = project
        self._result = {'not_found_common_types':0,'correct_common_types':0,'not_found_aggr_types':0,'correct_aggr_types':0}
        if result_file is not None:
            self._result_file = result_file
            self.preload_results()
        
    def compare_type_info(self):
        #Save result
        self.save_result()
        for current_class in self._dynamic_types_info.keys():
            node = self.get_class_by_full_name(current_class)
            if node is None:
                    continue
            for attrname in self._dynamic_types_info[current_class][1].keys():
                common_type = self.get_type("CommonType",node,attrname)
                aggr_type = self.get_type("AggregatedType",node,attrname)
                for type in self._dynamic_types_info[current_class][1][attrname]['common_type']:
                    if type in common_type:
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
    def __init__(self, project_tag, in_file, preload_file, skip_classes=(), delay=5):
        TypesComparator.__init__(self, in_file,project_tag,preload_file)
        self._dbg = CSUDbg(project_mark=project_tag, skip_classes=skip_classes, delay=delay)
        self._dbg.set_trace()
        curr_dir = os.getcwd()
        try:
            self.run()
        except SystemExit:
            """ Catching sys.exit """
            pass
        os.chdir(curr_dir)
        self._dbg.disable_trace()
        used_classes = self._dbg.get_used_classes()
        self._dynamic_types_info = used_classes
        self.compare_type_info()
        print len(self._dynamic_types_info.keys()), self.get_num_of_classes()
        res =  self.get_result()
        print "Correctly detected common types: ",res['correct_common_types']
        print "Correctly detected aggregated types: ",res['correct_aggr_types']
        print "Not correctly detected common types: ",res['not_found_common_types']
        print "Not correctly detected aggregated types: ",res['not_found_aggr_types']
        print "Success percentage: ",(res['correct_common_types']+res['correct_aggr_types'])*100.0/(res['correct_common_types']+res['correct_aggr_types']+res['not_found_common_types']+res['not_found_aggr_types']),"%"
                        

class LogilabObjectTracer(ObjectTracer):
    
    def __init__(self, in_file, preload_file):
        ObjectTracer.__init__(self,'logilab', in_file ,preload_file,skip_classes=(Const))
        
    def run(self):
        main.Run(sys.argv[1:])

class TwistedObjectTracer(ObjectTracer):
    
    def __init__(self, in_file,preload_file):
        ObjectTracer.__init__(self,'twisted', in_file ,preload_file)
        
    def run(self):
        twisted_ftpclient.run()
        
class PylintObjectTracer(ObjectTracer):
    
    def __init__(self, in_file, preload_file):
        ObjectTracer.__init__(self,'pylint', in_file ,preload_file,skip_classes=(Const))
        
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
    
    def __init__(self, in_file, preload_file,work_dir):
        import sys
        sys.setrecursionlimit(10000)
        from bzrlib.lazy_regex import LazyRegex
        self._work_dir = work_dir
        ObjectTracer.__init__(self,'bzrlib', in_file ,preload_file, skip_classes=(LazyRegex), delay=20)
        
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
    def __init__(self,args):
        ASTNGHandler.__init__(self,args)
        self.run()
    def run(self):
        linker = CFGLinker(self.project)
        linker.visit(self.project)