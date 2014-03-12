'''
Created on 08.04.2012

@author: bluesbreaker
'''

from logilab.common.configuration import ConfigurationMixIn
from pylint.pyreverse.main import OPTIONS
from CSUStAn.astng.simple import NamesCheckLinker
from CSUStAn.reflexion.rm_tools import ReflexionModelVisitor,HighLevelModelDotGenerator,SourceModelXMLGenerator
from CSUStAn.ucr.builder import UCRBuilder
from CSUStAn.ucr.visual import ClassHierarchyVisualizer
from CSUStAn.ucr.handling import ClassIRHandler
from CSUStAn.ucr.visual import UCRVisualizer
from CSUStAn.ucfr.builder import UCFRBuilder
from CSUStAn.ucfr.handling import FlatUCFRSlicer,ClassUCFRSlicer
from CSUStAn.tracing.class_tracer import *
from CSUStAn.ucfr.visual import UCFRVisualizer, ExecPathVisualizer,ExecPathCallsSearch
from CSUStAn.cross.visual import ExecPathObjectSlicer
from CSUStAn.cross.handling import DataflowLinker
from CSUStAn.ucr.handling import PotentialSiblingsCounter,InheritanceSlicer
from CSUStAn.ucfr.handling import UCFRHandler


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
        

    
    
class BigClassAnalyzer(UCFRHandler, ClassIRHandler):
    """
        Analyzes classes responsibility and finds "big" classes, that carries about too many things.
        These classes could be "God objects" or just overweighted with data.
        Also winds big and complex methods in classes.
    """
    
    
    def __init__(self, ucr_xml, cfg_xml):
        UCFRHandler.__init__(self, cfg_xml)
        ClassIRHandler.__init__(self, ucr_xml)
        self.run()
    
    def run(self):
        self.__counter = 1
        self.__report = ""
        self.for_each_class(self.process_class())
        print self.__report
        
    def process_class(self):
        def process_class_internal(c):
            print "Processing class " + c.get("name") + " (" + str(self.__counter) + "/" + str(self.get_num_of_classes()) + ")"
            self.__counter += 1
            attrs = len(self.handle_attrs(c))
            if attrs > 15:
                self.__report += "\nClass " + c.get("name") + " has potential problem with too many fields (" + str(attrs) + "). Maybe you should divide this class into some smaller?"
            methods = 0
            for method in c.iter("Method"):
                methods += 1
                args = len([x.get("name") for x in method.iter("Arg")])
                if args > 7:
                    self.__report += "\nClass " + c.get("name") + " has method " + method.get("name") + "() with too many arguments (" + str(args) + "). Maybe some of it should be fields?"
                for cfg_method in self._cfg_tree.xpath("//Method[@ucr_id=\"" + c.get("id") + "\" and @name=\"" + method.get("name") + "\"]"):
                    flows = len([x.get("name") for x in cfg_method.iter("Flow")])
                    blocks = len([x.get("name") for x in cfg_method.iter("Block")])
                    if blocks > 10:
                        self.__report += "\nClass " + c.get("name") + " has method " + method.get("name") + "() with too many blocks in control flow (" + str(blocks) + "). Maybe you need to extract some to new method?"
                    if flows > 20:
                        self.__report += "\nClass " + c.get("name") + " has method " + method.get("name") + "() with too many flows (" + str(flows) + "). Maybe you need to extract a new method?"
                    if float(flows)/float(blocks) > 2.0:
                        self.__report += "\nClass " + c.get("name") + " has method " + method.get("name") + "() with complex control flow. Maybe you need to extract a new methods or simplify this?"
            if methods > 30 or (methods - 2*attrs > 10 and attrs > 5) :
                self.__report += "\nClass " + c.get("name") + " has too many methods. Looks like it has too many responsibilities. Maybe you should divide it?"
        
        return process_class_internal
    

class GreedyFunctionsAnalyzer(UCFRHandler, ClassIRHandler):
    """
        Analyzes functions for being "greedy", i.e. using some field or variable very much.
        These greedy functions might be moved to another class, which is used much.
    """
    
    __GREEDY_METHOD = "\nMethod {0} from class {1} is probably greedy and should be moved to {2}."
    __MB_GREEDY_METHOD = ("\nMethod {0} from class {1} may be greedy. It uses too much variable {2} ({3}). But class of variable wasn't recognized."
                            "\nIt may happens when class isn't in project or variable of this class wasn't found or it is external module, not a class.\n")
    
    def __init__(self, ucr_xml, cfg_xml):
        UCFRHandler.__init__(self, cfg_xml)
        ClassIRHandler.__init__(self, ucr_xml)
        self.run()
        
    def run(self):
        self.__counter = 1
        self.__report = ""
        self.for_each_method(self.process_method())
        print self.__report
    
    def process_method(self):
        def process_method_internal(method):
            print "Processing method {0} from class {1} ({2}/{3})".format(method.get("name"), method.get("parent_class"), str(self.__counter), self.get_num_of_methods())
            self.__counter += 1
            classes_used = {}
            names_used = {}
            for get_attr in method.xpath("Block/Call/Getattr"):
                label = get_attr.get("label")
                if label != "self" and label != "this": 
                    if label in names_used:
                        names_used[label] += 1
                    else:
                        names_used[label] = 1
                target = get_attr.get("Target")
                if target != None:
                    targetClass = target.get("TargetClass")
                    if targetClass != None:
                        ucr_id = targetClass.get("ucr_id")
                        if ucr_id in classes_used:
                            classes_used[ucr_id] += 1
                        else:
                            classes_used[ucr_id] = 1
            for k, v in classes_used.items():
                if v > 5:
                    self.__report += self.__GREEDY_METHOD.format(method.get("name"), method.get("parent_class"), self.get_class_by_id(k).get("name"))
            for k, v in names_used.items():
                if v > 7:
                    self.__report += self.__MB_GREEDY_METHOD.format(method.get("name"), method.get("parent_class"), k, str(v))
            
        return process_method_internal
