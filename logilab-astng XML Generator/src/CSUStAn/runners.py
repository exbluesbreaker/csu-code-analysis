'''
Created on 08.04.2012

@author: bluesbreaker
'''

from logilab.common.configuration import ConfigurationMixIn
from pylint.pyreverse.main import OPTIONS
from CSUStAn.astng.simple import NamesCheckLinker
from CSUStAn.reflexion.rm_tools import ReflexionModelVisitor,HighLevelModelDotGenerator,SourceModelXMLGenerator
from CSUStAn.ucr.builder import UCRBuilder, PylintUCRBuilder
from CSUStAn.ucr.visual import ClassHierarchyVisualizer
from CSUStAn.ucr.handling import ClassIRHandler
from CSUStAn.ucr.visual import UCRVisualizer
from CSUStAn.ucfr.builder import UCFRBuilder
from CSUStAn.ucfr.handling import FlatUCFRSlicer,ClassUCFRSlicer, ExecRouteSearch
from CSUStAn.tracing.tracers import *
from CSUStAn.ucfr.visual import UCFRVisualizer, ExecPathVisualizer,ExecPathCallsSearch
from CSUStAn.cross.visual import ExecPathObjectSlicer
from CSUStAn.cross.handling import DataflowLinker, UnreachableCodeSearch,InstanceInitSlicer
from CSUStAn.ucr.handling import PotentialSiblingsCounter,InheritanceSlicer
from CSUStAn.ucfr.handling import UCFRHandler
from lxml import etree
import time


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
	self.__make_connections()
        self.for_each_class(self.process_class())
        print self.__report

    def __make_connections(self):
        self.__ucfr_methods = {}
        for method in self._methods:
	    ucr_id = method.get("ucr_id") 
	    if ucr_id in self.__ucfr_methods:
	        self.__ucfr_methods[ucr_id].append(method)
	    else:
	        self.__ucfr_methods[ucr_id] = [method]

    def __get_method(self, ucr_id, name):
        for method in self.__ucfr_methods[ucr_id]:
	    if method.get("name") == name:
	        yield method
        
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
                if args > 5:
                    self.__report += "\nClass " + c.get("name") + " has method " + method.get("name") + "() with too many arguments (" + str(args) + "). Maybe some of it should be fields?"
                for cfg_method in self.__get_method(c.get("id"), method.get("name")):
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
    
    def __init__(self, ucr_xml, cfg_xml, cfg_id, creation_count):
        UCFRHandler.__init__(self, cfg_xml)
        ClassIRHandler.__init__(self, ucr_xml)
        self.__method_id = cfg_id
        self.__count = {}
        self.__creation_count = int(creation_count)
        self.run()
    
    def run(self):
        self.__counter = 1
        self.__report = ""
        self.__count = {}
        self.__total = 0
	self.__total_methods = 0
        self.for_each_class(self.process_class())
        for clazz, cnt in self.__count.items():
            if (cnt <= self.__creation_count) and (cnt > 0):
                self.__report += "\nClass {className} created only in few methods: {methods}".format(className = clazz, methods = cnt)
                self.__total += cnt
        print self.__report
        print "Total classes with limited creation counts is {0}".format(self.__total)
	print "Total methods count is {0}".format(self.__total_methods)
        
    def process_class(self):
        def process_class_internal(c):
	    methods_count = len([meth.get("name") for meth in c.iter("Method")])
            print "Processing class " + c.get("name") + " (" + str(self.__counter) + "/" + str(self.get_num_of_classes()) + "), methods - " + str(methods_count)
	    self.__total_methods += methods_count
	    short_name = c.get("name").split(".")[-1:]
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
                    self.__report += "\nClass {clazz} created in {method_name} (target id {method_id}) from {parent_class}".format(clazz = c.get("name"), method_name = method_name, method_id = target.get("cfg_id") if target != None else "", parent_class = class_name)
                    self.__count[c.get("name")] += 1
                for tc in self._cfg_tree.xpath("//Method/Block/Call/Direct[contains('{class_name}', @name)]/Target/TargetClass[@label='{class_name}']".format(class_name = c.get("name"))):
                    target = tc.getparent()
                    method_name = tc.getparent().getparent().getparent().getparent().getparent().get("name")
                    class_name = tc.getparent().getparent().getparent().getparent().getparent().get("parent_class")
                    self.__report += "\nClass {clazz} created in {method_name} (target id {method_id}) from {parent_class}".format(clazz = c.get("name"), method_name = method_name, method_id = target.get("cfg_id"), parent_class = class_name)
                    self.__count[c.get("name")] += 1
        
        return process_class_internal

class GreedyFunctionsAnalyzer(UCFRHandler, ClassIRHandler):
    """
        Analyzes functions for being "greedy", i.e. using some field or variable very much.
        These greedy functions might be moved to another class, which is used much.
    """
    
    __GREEDY_METHOD = "\nMethod {0} from class {1} is probably greedy and should be moved to {2}."
    __MB_GREEDY_METHOD = ("\nMethod {0} from class {1} may be greedy. It uses too much variable {2} ({3}). But class of variable wasn't recognized."
                            "\nIt may happens when class isn't in project or variable of this class wasn't found or it is external module, not a class.\n")
    
    def __init__(self, ucr_xml, cfg_xml, call_count):
        UCFRHandler.__init__(self, cfg_xml)
        ClassIRHandler.__init__(self, ucr_xml)
        self.__call_count = int(call_count)
        self.run()
        
    def run(self):
        self.__counter = 1
        self.__report = ""
        self.__total = 0
        self.__total_names = 0
        self.for_each_method(self.process_method())
        print self.__report
        print "Total greedy methods is {0}".format(self.__total)
        print "Total probably greedy methods {0}".format(self.__total_names)
    
    def process_method(self):
        def process_method_internal(method):
            print "Processing method {0} from class {1} ({2}/{3})".format(method.get("name"), method.get("parent_class"), str(self.__counter), self.get_num_of_methods())
            self.__counter += 1
            classes_used = {}
            names_used = {}
            for get_attr in method.xpath("./Block/Call/Getattr"):
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
                if v > self.__call_count:
                    self.__report += self.__GREEDY_METHOD.format(method.get("name"), method.get("parent_class"), self.get_class_by_id(k).get("name"))
                    self.__total += 1
            for k, v in names_used.items():
                if v > self.__call_count:
                    self.__report += self.__MB_GREEDY_METHOD.format(method.get("name"), method.get("parent_class"), k, str(v))
                    self.__total_names += 1
            
        return process_method_internal

class BigClassAnalyzerJavaAst(UCFRHandler, ClassIRHandler):
    """
        Analyzes classes responsibility and finds "big" classes, that carries about too many things.
        These classes could be "God objects" or just overweighted with data.
        Also winds big and complex methods in classes.
    """
    
    def __init__(self, ast_xml):
        parser = etree.XMLParser(remove_blank_text=True)
        self._ast_tree = etree.parse(ast_xml, parser)
        self.run()
    
    def run(self):
        self.__counter = 1
        self.__report = ""
	self.__classes = {}
	self.find_classes()
        self.process_classes()
        print self.__report
        
    def find_classes(self):
        for node in self._ast_tree.iter("compilation_unit"):
	    package = ""
	    for package_node in node.iter("package"):
                package = self.get_package_name(package_node)
	    for clazz in node.xpath("./definitions/class"):
	        current_class_name = package+"."+clazz.get("name")
	        self.__classes[current_class_name] = clazz
		self.find_inner_classes(clazz, current_class_name)
            
    def get_package_name(self, package_tree):
        for child in package_tree.iterchildren("member_select", "identifier"):
	    prefix = self.get_package_name(child)
	    if prefix != None and len(prefix) > 0:
	        return prefix + "." + child.get("name")
	    else:
	        return child.get("name")

    def find_inner_classes(self, clazz, current_name):
        for child in clazz.iterchildren():
	    if "class" == child.tag:
	        inner_name = current_name + "." + child.get("name")
	        self.__classes[inner_name] = child
		self.find_inner_classes(child, inner_name)
	    else:
	        self.find_inner_classes(child, current_name)

    def process_classes(self):
        counter = 0
        for clazz, node in self.__classes.items():
	    counter += 1
	    print "Processing class {0} ({1}/{2})".format(clazz, counter, len(self.__classes))
	    fields = len([v.get("name") for v in node.xpath("./body/variable")])
	    if fields > 15:
	        self.__report += "\nClass {0} has potential problem with too many fields ({1}). Maybe you should divide this class into some smaller?".format(clazz, fields)
	    methods = 0
            for method in node.xpath("./body/method"):
	        methods += 1
		args = len([v.get("name") for v in method.xpath("./parameters/variable")])
                if args > 5:
		    self.__report += "\nClass {0} has method {1}() with too many arguments ({2}). Maybe some of it should be fields?".format(clazz, method.get("name"), args)
		flows = 0
		blocks = 0
		for i in method.xpath("./block//*[self::for_loop or self::enhanced_for_loop]"): flows += 3
		for i in method.xpath("./block//*[self::while_loop or self::do_while_loop]"): flows += 3
		for i in method.xpath("./block//if"): flows += 2
		for i in method.xpath("./block//*[self::then_part or self::else_part]"): flows += 1
		for i in method.xpath("./block//*[self::try or self::catch or self::finally]"): flows += 2
		for i in method.xpath(".//*[self::block or self::body]"): blocks += 1
                if blocks > 10:
                    self.__report += "\nClass {0} has method {1}() with too many blocks in control flow ({2}). Maybe you need to extract some to new method?".format(clazz, method.get("name"), blocks)
                if flows > 20:
                    self.__report += "\nClass {0} has method {1}() with too many flows ({2}). Maybe you need to extract a new method?".format(clazz, method.get("name"), flows)
                if blocks != 0 and float(flows)/float(blocks) > 2.0:
                    self.__report += "\nClass {0} has method {1}() with complex control flow. Maybe you need to extract a new methods or simplify this?".format(clazz, method.get("name"))
            if methods > 30 or (methods - 2*fields > 10 and fields > 5):
	        self.__report += "\nClass {0} has too many methods. Looks like it has too many responsibilities. Maybe you should divide it?".format(clazz)
        
def current_time():
    return int(round(time.time() * 1000))

class BCAChecker(BigClassAnalyzer):
    
    def __init__(self, ucr_xml, cfg_xml):
        UCFRHandler.__init__(self, cfg_xml)
        ClassIRHandler.__init__(self, ucr_xml)
	t = current_time()
	for i in xrange(0, 10000):
            self.run()
	    print "*** {0} out of 10 000 ***".format(i)
	t = current_time() - t
	print "Time in millis:", t

class BCAAstChecker(BigClassAnalyzerJavaAst):
    
    def __init__(self, ast_xml):
        parser = etree.XMLParser(remove_blank_text=True)
        self._ast_tree = etree.parse(ast_xml, parser)
	t = current_time()
	for i in xrange(0, 10000):
            self.run()
	    print "*** {0} out of 10 000 ***".format(i)
	t = current_time() - t
	print "Time in millis:", t
