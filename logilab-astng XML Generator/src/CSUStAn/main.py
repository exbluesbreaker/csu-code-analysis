# -*- coding: utf-8 -*-
'''
Created on 19.08.2011

@author: bluesbreaker
'''

import importlib
from CSUStAn.runners import ReflexionModelRunner
from CSUStAn.reflexion.rm_tools import RegexMapper

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


    
        










    
scons_map = {'Job':['SCons.Job'],
                   'Node.FS':['SCons.Node.FS'],
                   'Action':['SCons.Action'],
                   'Builder':['SCons.Builder'],
                   'SConf':['SCons.SConf'],
                   'Scanner':[u'SCons\.Scanner.*'],
                   'Script':[u'SCons\.Script.*'],
                   'Taskmaster':['SCons.Taskmaster'],
                   'Util':['SCons.Util'],
                   'Variables':[u'SCons\.Variables.*'],
                   'Environment':['SCons.Environment'],
                   'Executor':['SCons.Executor'],
                   'Tool.packaging':[u'SCons\.Tool\.packaging.*'],
                   'Tool':[u'SCons\.Tool(?!\.packaging)'],
                   'Platform':[u'SCons\.Platform.*']}
scons_hm_model = [('Script', 'Taskmaster'),
                    ('Taskmaster', 'SConf'),
                    ('Taskmaster', 'Builder'),
                    ('SConf', 'Environment'),
                    ('SConf', 'Util'),
                    ('Builder', 'Executor'),
                    ('Builder', 'Variables'),
                    ('Builder', 'Scanner'),
                    ('Builder', 'Util'),
                    ('Builder', 'Environment'),
                    ('Scanner', 'Action'),
                    ('Executor', 'Action'),
                    ('Action', 'Util'),
                    ('Action', 'Variables'),
                    ('Action', 'Job'),
                    ('Job', 'Util'),
                    ('Job', 'Node.FS')]

logilab_map = {'TreePostProcessing':['logilab.astng.inspector','logilab.astng.inference'],
               'Manager':['logilab.astng.manager'],
               'Nodes':[u'logilab\.astng\.node.*','logilab.astng.scoped_nodes','logilab.astng.bases','logilab.astng.mixins'],
               'PrivateNodes':[u'logilab\.astng\._nodes.*','logilab.astng.patchcomptransformer'],
               'Builder':[u'logilab\.astng\..*build.*'],
               'NodesHandling':['logilab.astng.protocols'],
               'TreesHandling':['logilab.astng.utils','logilab.common.tree','logilab.common.visitor'],
               'DatabaseHandling':[u'logilab\.common\..*db.*','logilab.common.sqlgen','logilab.common.table'],
               'Cache':['logilab.common.cache'],
               'ChangelogHandling':['logilab.common.changelog'],
               'CommandLineHandling':[u'logilab\.common\.cl.*','logilab.common.optik_ext','logilab.common.optparser'],
               'Configuration':['logilab.common.configuration'],
               'CORBAUtils':['logilab.common.corbautils'],
               'Daemon':['logilab.common.daemon'],
               'Date':['logilab.common.date'],
               'Debugger':['logilab.common.debugger'],
               'Decorators':['logilab.common.decorators','logilab.common.deprecation'],
               'FileUtils':['logilab.common.fileutils'],
               'Output':['logilab.common.graph','logilab.common.html','logilab.common.pdf_ext','logilab.common.vcgutils'],
               'Logging':['logilab.common.logging_ext'],
               'SourceHandling':['logilab.common.interface','logilab.common.modutils'],
               'Proc':['logilab.common.proc'],
               'Remote':['logilab.common.pyro_ext','logilab.common.xmlrpcutils'],
               'Test':['logilab.common.pytest','logilab.common.testlib'],
               'TextProcessing':['logilab.common.textutils'],
               'Sphinx':['logilab.common.sphinx_ext','logilab.common.sphinxutils'],
               'Ureports':[u'logilab\.common\.ureports.*']}

logilab_hm_model = [('Manager', 'TreePostProcessing'),
                    ('Manager', 'Cache'),
                    ('Manager', 'Configuration'),
                    ('Manager', 'Output'),
                    ('Manager', 'Daemon'),
                    ('Manager', 'CommandLineHandling'),
                    ('Manager', 'Builder'),
                    ('Builder', 'TreesHandling'),
                    ('Builder', 'SourceHandling'),
                    ('Builder', 'TextProcessing'),
                    ('TreesHandling', 'NodesHandling'),
                    ('NodesHandling', 'Nodes'),
                    ('TreesHandling', 'Nodes'),
                    ('Nodes', 'PrivateNodes'),
                    ('Daemon', 'Proc'),
                    ('Proc', 'Daemon'),
                    ('Sphinx', 'DatabaseHandling')
                    ]

#scons_mapper = RegexMapper(mapping=scons_map)
#scons_runner = ReflexionModelRunner('SCons',scons_hm_model,scons_mapper)
logilab_mapper = RegexMapper(mapping=logilab_map)
scons_runner = ReflexionModelRunner('logilab',logilab_hm_model,logilab_mapper)
#scons_runner = ReflexionModelRunner(sys.argv[1:])
#main_xml_root = etree.Element("PythonSourceTree")
#ns_xml_root = etree.Element("PythonNamespaces")
#main_prj = scons_runner.project
#make_tree(main_xml_root,scons_runner.project)
#handle = etree.tostring(main_xml_root, pretty_print=True, encoding='utf-8', xml_declaration=True)
#main_file = "./"+sys.argv[-1]+".xml"    
#applic = open(main_file, "w")
#applic.writelines(handle)
#applic.close()
#print "bad imports - ",bad_imports,"bad from imports - ",bad_from_imports,"good - ",good_imports
#print "from imports - ",from_imports,"from * imports - ",from_allimports, "from imports of module - ", from_modname_imports
#print "not found in from imports - ", unknown_name_from_module