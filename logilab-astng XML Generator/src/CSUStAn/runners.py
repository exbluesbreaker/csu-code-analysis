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
from CSUStAn.reflexion.rm_tools import ReflexionModelVisitor,HighLevelModelDotGenerator,SourceModelXMLGenerator
from lxml import etree

# must be refactored
from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import *
import re
import pydot
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
    
    def __init__(self, args,process_candidates=False):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        self._process_candidates = process_candidates
        insert_default_options()
        self.manager = ASTNGManager()
        self.register_options_provider(self.manager)
        args = self.load_command_line_configuration()
        self.run(args)
    
    def _process_node(self,node,attrs,duck_dict=None):
        if(duck_dict is None):
            duck_dict = {}
        if isinstance(node, Getattr):
            if(node.expr.as_string()=="self"):
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
                        duck_dict[node.attrname] = {'attrs':Set([]),'methods':Set([])}
                    if isinstance(node.parent.parent,CallFunc):
                        #we get info about attr's method
                        duck_dict[node.attrname]['methods'].add(node.parent.attrname)
                    else:
                        #we get info about attr's attr
                        duck_dict[node.attrname]['attrs'].add(node.parent.attrname)
        for child in node.get_children():
            duck_dict = self._process_node(child,attrs,duck_dict)
        return duck_dict

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
        mapper = {}
        root = etree.Element("Classes")
        for obj in diadefs[1].objects:
            self._all_classes +=1
            node = etree.Element("Class",name=obj.title,id=str(obj.fig_id))
            mapper[obj] = node
            root.append(node)
            for attr in obj.attrs:
                # drop type specification in attr name, if it exists
                node.append(etree.Element('Attr',name=re.search('[^ :]*',attr).group(0),modifier='public'))
            attr_names = [re.search('[^ :]*',s).group(0) for s in obj.attrs]
            attr_names+= [m.name for m in obj.methods]
            duck_dict = None
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
                # check self access in method and generate information about class attrs 
                if(self._process_candidates):
                    duck_dict =  self._process_node(meth,attr_names,duck_dict)
            if(duck_dict is None):
                continue
            duck_node = etree.Element("Duck")
            node.append(duck_node)
            for attr in duck_dict.keys():
                self._all_ducks += 1
                duck_attr_node = etree.Element('DuckAttr',name=attr)
                for sub_attr in duck_dict[attr]['attrs']:
                    duck_attr_node.append(etree.Element('ProbAttr',name=sub_attr))
                for sub_attr in duck_dict[attr]['methods']:
                    duck_attr_node.append(etree.Element('ProbMethod',name=sub_attr))
                duck_node.append(duck_attr_node)
        for rel in diadefs[1].relationships['specialization']:
            mapper[rel.from_object].append(etree.Element('Parent',name=rel.to_object.title,id=str(rel.to_object.fig_id)))
        f = open('test.xml','w')
        f.write(etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
        print self._good_gettatr,self._bad_gettatr
        print self._all_ducks
        print self._all_classes
        
class ClassIRHandler:
    # Process XML class IR
    _tree = None
    _classes = None
    def __init__(self, args):
        if(len(args)!=1):
            print "usage <> <file name>"
            exit(0)
        self._tree = etree.parse(args[0])
        self._classes = [node for node in self._tree.iter("Class")] 
    def get_methods(self,node):
        return Set([meth.get("name") for meth in node.iter("Method")])
    def get_parents(self,node):
        return [self._tree.xpath("//Class[@id="+parent.get("id")+"]")[0] for parent in node.iter("Parent")]

class FieldCandidateFinder(ConfigurationMixIn,ClassIRHandler):
    # scan classes description for candidate for class's field
    
    options = OPTIONS
    _successes = 0
    _fails = 0
    _tree = None
    _complete_signatures = {}
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        ClassIRHandler.__init__(self, args)
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
    _methods = {}
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        ClassIRHandler.__init__(self, args)
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
        
       
        
