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
from CSUStAn.tracing.tracers import *
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
        self.forEachClass(self.process_class())
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
    
class ObjectCreationAnalysis(UCFRHandler, ClassIRHandler):
    """
        Analyzes conditions of places where instance of classes are created (constructors called).
    """
    
    def __init__(self, ucr_xml, cfg_xml, cfg_id):
        UCFRHandler.__init__(self, cfg_xml)
        ClassIRHandler.__init__(self, ucr_xml)
        self.__method_id = cfg_id
        self.__count = {}
        self.run()
    
    def run(self):
        self.__counter = 1
        self.__report = ""
        self.__count = {}
        self.forEachClass(self.process_class())
        for clazz, cnt in self.__count.items():
            if cnt <= 2 and cnt > 0:
                self.__report += "\nClass {className} created only in few methods: {methods}".format(className = clazz, methods = cnt)
        print self.__report
        
    def process_class(self):
        def process_class_internal(c):
            print "Processing class " + c.get("name") + " (" + str(self.__counter) + "/" + str(self.get_num_of_classes()) + ")"
            self.__counter += 1
            if c.get("name") not in self.__count.keys():
                self.__count[c.get("name")] = 0
            if self.__method_id != None and len(self.__method_id)>0:
                for direct in self._cfg_tree.xpath("//Method[@cfg_id='{cfg_id}']/Block/Call/Direct[@name='{class_name}']".format(cfg_id = self.__method_id, class_name = c.get("name"))):
                    target = direct.get("Target")
                    self.__report += "\nClass {clazz} created in {method_id}".format(clazz = c.get("name"), method_id = (target.get("cfg_id") if target != None else direct.get("name")))
                    self.__count[c.get("name")] += 1
            else:
                for direct in self._cfg_tree.xpath("//Method/Block/Call/Direct[@name='{class_name}']".format(class_name = c.get("name"))):
                    target = direct.get("Target")
                    method_name = direct.getparent().getparent().getparent().get("name")
                    class_name = direct.getparent().getparent().getparent().get("parent_class")
                    self.__report += "\nClass {clazz} created in {method_id} from {parent_class}".format(clazz = c.get("name"), method_id = target.get("cfg_id") if target != None else method_name, parent_class = class_name)
                    self.__count[c.get("name")] += 1
        
        return process_class_internal
