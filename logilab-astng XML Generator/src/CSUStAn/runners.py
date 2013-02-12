'''
Created on 08.04.2012

@author: bluesbreaker
'''

from logilab.common.configuration import ConfigurationMixIn
from logilab.astng.manager import astng_wrapper, ASTNGManager
from logilab.astng.inspector import Linker

from pylint.pyreverse.diadefslib import DiadefsHandler
from pylint.pyreverse.utils import insert_default_options
from pylint.pyreverse.main import OPTIONS
from pylint.pyreverse import writer
from CSUStAn.astng.simple import NamesCheckLinker
from CSUStAn.tracing.class_tracer import CSUDbg
from CSUStAn.reflexion.rm_tools import ReflexionModelVisitor,HighLevelModelDotGenerator,SourceModelXMLGenerator
from CSUStAn.tests import twisted_ftpclient, twisted_getpage, twisted_ptyserv, twisted_testlogging
from lxml import etree
from twisted.internet import reactor
from pylint.pyreverse import main
import subprocess

# must be refactored
from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import *
import re
import pydot
import os
from sets import Set

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
    _process_candidates = False
    _ducks_count = 0
    _found_ducks = 0
    _prob_used_classes = None
    _all_attrs_num = 0
    _complex_ducks = 0
    _assigned_ducks = 0
    _dbg_assattr_parents = None 
    _list_attrs = [attr for attr in dir([]) if not re.search('\A(?!_)',attr)]
    _list_methods = [attr for attr in dir([]) if re.search('\A(?!_)',attr)]
    _dict_attrs = [attr for attr in dir({}) if not re.search('\A(?!_)',attr)]
    _dict_methods = [attr for attr in dir({}) if re.search('\A(?!_)',attr)]
    _tuple_attrs = [attr for attr in dir(()) if not re.search('\A(?!_)',attr)]
    _tuple_methods = [attr for attr in dir(()) if re.search('\A(?!_)',attr)]
    _attr_iteration_cycles = 0
    
    def __init__(self, args,process_candidates=False):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        self._prob_used_classes = Set([])
        self._dbg_assattr_parents = Set([])
        self._process_candidates = process_candidates
        insert_default_options()
        self.manager = ASTNGManager()
        self.register_options_provider(self.manager)
        args = self.load_command_line_configuration()
        self.run(args)
      
    """ Extract information about class signature - attrs and methods, which it have """    
    def _compute_signature(self,node):
        if(hasattr(node, "csu_complete_signatures")):
            # node have been processed already
            return node.csu_complete_signatures
        else:
            node.csu_complete_signatures={}
        node.csu_complete_signatures['Attrs'] = Set([re.search('[^ :]*',attr).group(0) for attr in node.attrs])
        node.csu_complete_signatures['Methods'] = Set([meth.name for meth in node.methods])
        # class without parents
        if not hasattr(node, "csu_parents"):
            node.csu_parents = []
        parents = node.csu_parents
        for parent in parents:
            parent_signature = self._compute_signature(parent)
            # append all parents signatures
            node.csu_complete_signatures['Attrs'] |= parent_signature['Attrs']
            node.csu_complete_signatures['Methods'] |= parent_signature['Methods']
        return node.csu_complete_signatures
    
    """ Check body of cycle, which iterating over class's field"""
    def _check_cycle(self,node,iter_name,attr,duck_dict):
        if isinstance(node, Getattr):
            if(node.expr.as_string()==iter_name):
                if(not duck_dict[attr].has_key('element_signature')):
                           duck_dict[attr]['element_signature']={'attrs':Set([]),'methods':Set([])} 
                if isinstance(node.parent,CallFunc):
                    duck_dict[attr]['element_signature']['methods'].add(node.attrname)
                else:
                    duck_dict[attr]['element_signature']['attrs'].add(node.attrname)           
        for child in node.get_children():
            duck_dict = self._check_cycle(child,iter_name,attr,duck_dict)
        return duck_dict
    
    """ Extract information about class fields usage """
    def _extract_duck_info(self,node,attrs,duck_dict=None):
        if(duck_dict is None):
            duck_dict = {}
        if isinstance(node, Getattr):
            if(node.expr.as_string()=="self"):
                if isinstance(node.parent, For):
                    if(not duck_dict.has_key(node.attrname)):
                        self._ducks_count +=1
                        duck_dict[node.attrname] = {'attrs':Set([]),'methods':Set([]),'type':[],'complex_type':'Unknown','assigned':False}
                    self._attr_iteration_cycles +=1
                    if isinstance(node.parent.target, AssName):
                        print node.parent.as_string()
                        for body in node.parent.body:
                            duck_dict = self._check_cycle(body,node.parent.target.name,node.attrname,duck_dict)
                if(node.attrname not in attrs):
                    #print node.attrname,node.parent, node.fromlineno, node.root()
                    #print attrs
                    self._bad_gettatr+=1
                else:
                    self._good_gettatr+=1
                # if additional info about attr's field may be obtained
                if isinstance(node.parent, Getattr):
                    #init dict for attr
                    if(not duck_dict.has_key(node.attrname)):
                        self._ducks_count +=1
                        duck_dict[node.attrname] = {'attrs':Set([]),'methods':Set([]),'type':[],'complex_type':None,'assigned':False}
                    if isinstance(node.parent.parent,CallFunc):
                        #we get info about attr's method
                        duck_dict[node.attrname]['methods'].add(node.parent.attrname)
                    else:
                        #we get info about attr's attr
                        duck_dict[node.attrname]['attrs'].add(node.parent.attrname)
                # attr of complex type (list, dict, tuple etc.)
                elif isinstance(node.parent, Subscript):
                    if(not duck_dict.has_key(node.attrname)):
                        self._ducks_count +=1
                        duck_dict[node.attrname] = {'attrs':Set([]),'methods':Set([]),'type':[],'complex_type':'Unknown','assigned':False}
                    else:
                        duck_dict[node.attrname]['complex_type'] = 'Unknown'
                    if(isinstance(node.parent.parent,Getattr)):
                       # get some info about element of complex type
                       if(not duck_dict[node.attrname].has_key('element_signature')):
                           duck_dict[node.attrname]['element_signature']={'attrs':Set([]),'methods':Set([])}
                       if isinstance(node.parent.parent.parent,CallFunc):
                           duck_dict[node.attrname]['element_signature']['methods'].add(node.parent.parent.attrname)
                       else:
                           duck_dict[node.attrname]['element_signature']['attrs'].add(node.parent.parent.attrname)
        elif isinstance(node, AssAttr):
            if(node.expr.as_string()=="self"):
                if(not duck_dict.has_key(node.attrname)):
                    self._ducks_count +=1
                    self._assigned_ducks +=1
                    duck_dict[node.attrname] = {'attrs':Set([]),'methods':Set([]),'type':[],'complex_type':None,'assigned':True} 
                else:
                    if(not duck_dict[node.attrname]['assigned']):
                        duck_dict[node.attrname]['assigned'] = True
                        self._assigned_ducks+=1
                # DEBUG
                if (not node.parent.__class__.__name__ in self._dbg_assattr_parents):
                    self._dbg_assattr_parents |= Set([node.parent.__class__.__name__])
                    print node.parent.__class__.__name__
                    if(isinstance(node.parent, Tuple)):
                        print node.parent.as_string()
                # DEBUG END
                if(isinstance(node.parent, (Assign,AugAssign))):
                    if(isinstance(node.parent.value, (Tuple,Dict,List))):
                        duck_dict[node.attrname]['complex_type'] = node.parent.value.__class__.__name__ 
        for child in node.get_children():
            duck_dict = self._extract_duck_info(child,attrs,duck_dict)
        return duck_dict
    
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
        linker = Linker(project, tag=True)
        handler = DiadefsHandler(self.config)
        diadefs = handler.get_diadefs(project, linker)
        # Add inheritance information to nodes
        # csu_parents will contain links to all parents of class
        for rel in diadefs[-1].relationships['specialization']:
            if hasattr(rel.from_object, "csu_parents"):
                rel.from_object.csu_parents.append(rel.to_object)
            else:
                rel.from_object.csu_parents=[rel.to_object]
        bad_ducks = 0
        empty_ducks = 0
        # First pass for collecting "duck" information about fields 
        for obj in diadefs[-1].objects:
            self._compute_signature(obj)
            attr_names = [re.search('[^ :]*',s).group(0) for s in obj.attrs]
            self._all_attrs_num += len(attr_names)
            attr_names+= [m.name for m in obj.methods]
            duck_dict = None
            for meth in obj.methods:
                # check self access in method and generate information about class attrs 
                if(self._process_candidates):
                    duck_dict =  self._extract_duck_info(meth,attr_names,duck_dict)
            # add duck information to classes
            obj.ducks=duck_dict
        successes = 0
        #Second pass  for processing "duck" information and generate information about types
        for current_class in diadefs[-1].objects:
            if (current_class.ducks is None):
                continue
            for duck in current_class.ducks.keys():
                if(current_class.ducks[duck]['complex_type']):
                    self._complex_ducks +=1
                    #self._found_ducks+=1
                    # duck is complex type, nothing to do with it
                    # TODO recursively complex types
                    if current_class.ducks[duck].has_key('element_signature'):
                        # search for class of element is needed 
                        duck_attrs = current_class.ducks[duck]['element_signature']['attrs']
                        duck_methods = current_class.ducks[duck]['element_signature']['methods']
                    else:
                        # duck of complex type and no duck info about element
                        empty_ducks += 1
                        continue
                else:
                    duck_attrs = current_class.ducks[duck]['attrs']
                    duck_methods = current_class.ducks[duck]['methods']
                # ignore empty ducks
                if((not duck_attrs) and (not duck_methods)):
                    empty_ducks += 1
                    continue
                duck_found = False
                for field_candidate in diadefs[-1].objects:
                    complex_type = self._check_complex_type(duck_attrs, duck_methods)
                    if(complex_type):
                        #DEBUG
                        if(current_class.ducks[duck]['complex_type']):
                            if((current_class.ducks[duck]['complex_type'] != complex_type) 
                               and (current_class.ducks[duck]['complex_type'] !='Unknown')):
                                print current_class.ducks[duck]['complex_type'], complex_type
                        #END DEBUG
                        current_class.ducks[duck]['complex_type'] = complex_type
                        if(not duck_found):
                            self._found_ducks+=1
                            duck_found = True
                    if(all(attr in field_candidate.csu_complete_signatures['Attrs'] for attr in duck_attrs) and all(method in field_candidate.csu_complete_signatures['Methods'] for method in duck_methods)):
                        current_class.ducks[duck]['type'].append(field_candidate)
                        successes += 1
                        self._prob_used_classes |= Set([field_candidate.fig_id])
                        if(not duck_found):
                            self._found_ducks+=1
                            duck_found = True
                #check if duck not found at all
                if(not duck_found):
                    bad_ducks += 1
                    print "Bad duck - ",duck_attrs, duck_methods     
        print "Bad ducks ", bad_ducks
        print "Empty ducks ", empty_ducks                    
        print "Numbers of ducks: ", self._ducks_count
        print "Numbers of ducks with assignment in class: ", self._assigned_ducks
        print "Numbers of ducks with complex type: ", self._complex_ducks
        print "Found ducks: ",self._found_ducks, " percentage: ",round(100*float(self._found_ducks)/self._ducks_count,1), " %"
        print "Numbers of all attributes in project: ", self._all_attrs_num, " percentage of found attrs: ",round(100*float(self._found_ducks)/self._all_attrs_num,1), " %"
        print "Numbers of classes: ",len(diadefs[-1].objects)
        print "Probably used (as field) classes: ",len(self._prob_used_classes)," percentage: ",round(100*float(len(self._prob_used_classes))/len(diadefs[-1].objects),1), " %"
        
        # result XML generation
        mapper = {}
        root = etree.Element("Classes")
        for obj in diadefs[-1].objects:
            self._all_classes +=1
            node = etree.Element("Class",name=obj.title,id=str(obj.fig_id),label=obj.node.root().name)
            mapper[obj] = node
            root.append(node)
            for attrname in Set([re.search('[^ :]*',attr).group(0) for attr in obj.attrs]):
                attr_node = etree.Element('Attr',name=attrname,modifier='public')
                node.append(attr_node)
                if(obj.ducks and (attrname in obj.ducks)):
                    if obj.ducks[attrname]['complex_type']:
                        for prob_type in obj.ducks[attrname]['type']:
                            attr_node.append(etree.Element('AggregatedType',type=str(obj.ducks[attrname]['complex_type']),element=prob_type.title,id=str(prob_type.fig_id)))
                    else:
                        for prob_type in obj.ducks[attrname]['type']:
                            attr_node.append(etree.Element('CommonType',name=prob_type.title,id=str(prob_type.fig_id)))       
            for meth in obj.methods:
                meth_node = etree.Element('Method',name=meth.name,modifier='public')
                # This is needed for some native libs(pyx)
                if(meth.args.args == None):
                    continue
                for arg in meth.args.args:
                    # ignore self arg
                    if not arg.name == 'self':
                        meth_node.append(etree.Element('Arg',name=arg.name))
                node.append(meth_node)
        for rel in diadefs[-1].relationships['specialization']:
            mapper[rel.from_object].append(etree.Element('Parent',name=rel.to_object.title,id=str(rel.to_object.fig_id)))
        f = open('test.xml','w')
        f.write(etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
        #print self._good_gettatr,self._bad_gettatr
        #print self._all_ducks
        
        #print self._all_classes
        
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
    def get_attrs(self,node):
        return Set([attr.get("name") for attr in node.iter("Attr")])
    def get_attr(self,node, attrname):
        attrs = [attr for attr in node.iter("Attr") if (attr.get("name")==attrname)]
        if(len(attrs)==0):
            return None
        else:
            return attrs[0]
    def get_type(self,type_mark,node, attrname, type_set= None):
        if type_set is None:
            type_set = Set([])
        attr = self.get_attr(node, attrname)
        if attr is not None:
            type_set |= Set([self._id_dict[type.get("id")].get("label")+'.'+self._id_dict[type.get("id")].get("name") for type in attr.iter(type_mark)])
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
        print "Numbers of d _no_more_trace = Falseucks: ",len(ducks)
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
                        print "Not found aggr ", current_class, attrname, type
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
                        dt_info[c.get("name")][1][attr.get("name")]={'common_type':Set([]),'aggregated_type':Set([])}
                    for ct in attr.iter("CommonType"):
                        dt_info[c.get("name")][1][attr.get("name")]['common_type'].add(ct.get("name"))
                    for at in attr.iter("AggregatedType"):
                        dt_info[c.get("name")][1][attr.get("name")]['aggregated_type'].add(at.get("name")) 
        self._preload_dt_info = dt_info
             
            
    def get_result(self):
        return self._result.copy()
                        

class LogilabObjectTracer(TypesComparator):
    
    def __init__(self, in_file, preload_file):
        TypesComparator.__init__(self, in_file,'logilab',preload_file)
        self._dbg = CSUDbg(project_mark='logilab')
        self._dbg.set_trace()
        self.run()
        
    def run(self):
        main.Run(sys.argv[1:])
        self._dbg.disable_trace()
        #print self._dbg.get_classes_usage() 
        used_classes = self._dbg.get_used_classes()
        self._dynamic_types_info = used_classes
        self.compare_type_info()
        print len(self._dynamic_types_info.keys()), self.get_num_of_classes()
        print self.get_result()
        #print used_classes
        #for key, value in sorted(used_classes.iteritems(), key=lambda (k,v): (v,k)):
        #    print "%s: %s" % (key, value)
        #print len(used_classes.keys())

class TwistedObjectTracer(TypesComparator):
    
    def __init__(self, in_file,preload_file):
        TypesComparator.__init__(self, in_file,'twisted',preload_file)
        self._dbg = CSUDbg(project_mark='twisted',preload_dt_info=self._preload_dt_info)
        self._dbg.set_trace()
        self.run()
        
    def run(self):
        #twisted_ftpclient.run()
        #twisted_getpage.get_page("http://en.wikipedia.org/wiki/Main_Page")
        #twisted_ptyserv.run()
        #twisted_testlogging.run()
        subprocess.call(["python2.7","/home/bluesbreaker/Development/csu-code-analysis/logilab-astng\ XML\ Generator/src/CSUStAn/tests/twisted_ftpclient.py"])
        self._dbg.disable_trace()
        used_classes = self._dbg.get_used_classes()
        self._dynamic_types_info = used_classes
        self.compare_type_info()
        print len(self._dynamic_types_info.keys()), self.get_num_of_classes()
        print self.get_result()
       
        
