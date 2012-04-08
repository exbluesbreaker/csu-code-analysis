# -*- coding: utf-8 -*-
'''
Created on 19.08.2011

@author: bluesbreaker
'''

import importlib
from CSUStAn.runners import ReflexionModelRunner

if __name__ == '__main__':
    pass


'''Names, which not found in namespace of module, from which import is'''
unknown_name_from_module = 0


                



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
hm_model = [('SCons.Script', 'SCons.Taskmaster'),
                    ('SCons.Taskmaster', 'SCons.SConf'),
                    ('SCons.Taskmaster', 'SCons.Builder'),
                    ('SCons.SConf', 'SCons.Environment'),
                    ('SCons.SConf', 'SCons.Util'),
                    ('SCons.Builder', 'SCons.Executor'),
                    ('SCons.Builder', 'SCons.Variables'),
                    ('SCons.Builder', 'SCons.Scanner'),
                    ('SCons.Builder', 'SCons.Util'),
                    ('SCons.Builder', 'SCons.Environment'),
                    ('SCons.Scanner', 'SCons.Action'),
                    ('SCons.Executor', 'SCons.Action'),
                    ('SCons.Action', 'SCons.Util'),
                    ('SCons.Action', 'SCons.Variables'),
                    ('SCons.Action', 'SCons.Job'),
                    ('SCons.Job', 'SCons.Util'),
                    ('SCons.Job', 'SCons.Node.FS')]

pc = ReflexionModelRunner('SCons',hm_model,mapping)
#pc = ReflexionModelRunner(sys.argv[1:])
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