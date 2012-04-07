# -*- coding: utf-8 -*-
'''
Created on 19.08.2011

@author: bluesbreaker
'''


from logilab.common.configuration import ConfigurationMixIn
from pylint.pyreverse.utils import insert_default_options
from lxml import etree

from logilab.astng.manager import astng_wrapper, ASTNGManager
from logilab.astng.manager import Project

import importlib
from reflexion.rm_tools import RMHandler
import pydot


 
if __name__ == '__main__':
    pass




'''Names, which not found in namespace of module, from which import is'''
unknown_name_from_module = 0

'''Number of from m import *'''
from_allimports = 0
'''Number of from m import name'''
from_imports = 0
'''From imports of module'''
from_modname_imports = 0
                



'''Function, which compares namespace from ASTNG module node and
   from dir(module_name) after importing of this module.
   Function try to find all names from "real" module names in generated in ASTNG namespace.
   Returns number of names, which was not found'''                
def compare_namespaces(module_node):
    '''try to import modname'''
    '''FIXME Error recovery'''
    path = None
    module_node.unresolved = []
    try:
        module = importlib.import_module(module_node.name)
    except ImportError:
        return None
    names_list = dir(module)
    for name in names_list:
        if not name in module_node:
        #if(not find_in_all_namespaces(module_node, name)):
            module_node.unresolved.append(name)
            




class ReflexionModelXMLGenerator():
    def generate(self,project_name,rm_call_deps):
        root_tag = etree.Element(project_name)
        rm_tag = etree.Element("Reflexion_model")
        root_tag.append(rm_tag)
        for source,target in rm_call_deps.keys():
            dep_tag = etree.Element("Dependency")
            dep_tag.set("dep",source+","+target)
            for call in rm_call_deps[(source,target)]:
                call_tag = etree.Element("Call")
                call_tag.set("source_module",call[0])
                call_tag.set("target_module",call[1])
                call_tag.set("called_object",call[2])
                call_tag.set("source_fromlineno",str(call[3]))
                call_tag.set("source_scope",call[4])
                if(call[5] is not None):
                    call_tag.set("source_object",call[5])
                dep_tag.append(call_tag)
            rm_tag.append(dep_tag)
        return root_tag
    
class HighLevelModelDotGenerator():
    def generate(self,nodes,deps):
        graph = pydot.Dot(graph_type='digraph')
        node_dict = {}
        for node in nodes:
            dot_node = pydot.Node(node)
            graph.add_node(dot_node)
            node_dict[node] = dot_node
        for source, target in deps:
            graph.add_edge(pydot.Edge(node_dict[source], node_dict[target]))
        return graph
    
        










'''FIXME Bad name - no XML generated here'''
class LogilabXMLGenerator(ConfigurationMixIn):
    """"""
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        insert_default_options()
        self.manager = ASTNGManager()
        self.register_options_provider(self.manager)
        args = self.load_command_line_configuration()
        args = args[0:1]
        self.run(args)

    def run(self, args):
        """checking arguments and run project"""
        if not args:
            print self.help()
            return
        project = self.manager.project_from_files(args, astng_wrapper)
        self.project = project 
        linker = NamesCheckLinker(project, tag=True)
        link_imports(project, linker)
        '''FIXME get from file through command line'''
        mapping = ['SCons.Job',
                   'SCons.Node.FS',
                   'SCons.Action',
                   'SCons.Builder',
                   'SCons.SConf',
                   'SCons.Scanner',
                   'SCons.Script',
                   'SCons.Taskmaster',
                   'SCons.Util',
                   'SCons.Variables',
                   'SCons.Environment',
                   'SCons.Executor']
        hm_model = [('SCons.Script','SCons.Taskmaster'),
                    ('SCons.Taskmaster','SCons.SConf'),
                    ('SCons.Taskmaster','SCons.Builder'),
                    ('SCons.SConf','SCons.Environment'),
                    ('SCons.SConf','SCons.Util'),
                    ('SCons.Builder','SCons.Executor'),
                    ('SCons.Builder','SCons.Variables'),
                    ('SCons.Builder','SCons.Scanner'),
                    ('SCons.Builder','SCons.Util'),
                    ('SCons.Builder','SCons.Environment'),
                    ('SCons.Scanner','SCons.Action'),
                    ('SCons.Executor','SCons.Action'),
                    ('SCons.Action','SCons.Util'),
                    ('SCons.Action','SCons.Variables'),
                    ('SCons.Action','SCons.Job'),
                    ('SCons.Job','SCons.Util'),
                    ('SCons.Job','SCons.Node.FS')]
        rm_linker = ReflexionModelVisitor(project,mapping,hm_model)
        rm_linker.compute_rm()
        rm_linker.write_rm_to_png("SCons")
        xml_writer = ReflexionModelXMLGenerator()
        xml_root = xml_writer.generate("SCons", rm_linker._sm_call_deps)
        handle = etree.tostring(xml_root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        applic = open("SCons_sm.xml", "w")
        applic.writelines(handle)
        applic.close()
        dot_writer = HighLevelModelDotGenerator()
        graph = dot_writer.generate(mapping, hm_model)
        graph.write_png('SCons_high-level_model.png')
        
        """handler = DiadefsHandler(self.config)
        diadefs = handler.get_diadefs(project, linker)
        if self.config.output_format == "vcg":
            writer.VCGWriter(self.config).write(diadefs)
        else:
            writer.DotWriter(self.config).write(diadefs)"""    


pc = LogilabXMLGenerator(sys.argv[1:])
#main_xml_root = etree.Element("PythonSourceTree")
#ns_xml_root = etree.Element("PythonNamespaces")
#main_prj = pc.project
#make_tree(main_xml_root,pc.project)
#handle = etree.tostring(main_xml_root, pretty_print=True, encoding='utf-8', xml_declaration=True)
#main_file = "./"+sys.argv[-1]+".xml"    
#applic = open(main_file, "w")
#applic.writelines(handle)
#applic.close()
#print "bad imports - ",bad_imports,"bad from imports - ",bad_from_imports,"good - ",good_imports
#print "from imports - ",from_imports,"from * imports - ",from_allimports, "from imports of module - ", from_modname_imports
#print "not found in from imports - ", unknown_name_from_module