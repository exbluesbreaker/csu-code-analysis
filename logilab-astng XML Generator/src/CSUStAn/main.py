# -*- coding: utf-8 -*-
'''
Created on 19.08.2011

@author: bluesbreaker
'''

import importlib
import argparse
import sys
from CSUStAn.runners import ReflexionModelRunner,ClassIRRunner, FieldCandidateFinder, ClassHierarchyVisualizer, PotentialSiblingsCounter, LogilabObjectTracer
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
    for name in names_list:#scons_mapper = RegexMapper(mapping=scons_map)
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
               'Nodes':[u'logilab\.astng\..*node.*','logilab.astng.bases','logilab.astng.mixins','logilab.astng.patchcomptransformer'],
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
                    ('Manager', 'Configuration'),
                    ('Manager', 'Output'),
                    ('Manager', 'Daemon'),
                    ('Manager', 'Builder'),
                    ('Builder', 'FileUtils'),
                    ('Builder', 'SourceHandling'),
                    ('TreesHandling', 'NodesHandling'),
                    ('NodesHandling', 'Nodes'),
                    ('TreesHandling', 'Nodes'),
                    ('Sphinx', 'DatabaseHandling')
                    ]

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument("-t", action="store",required=True, type=str, dest="type")
parser.add_argument("-o", action="store", type=str, default="out.xml", dest="out_file")
parser.add_argument("-i", action="store", type=str, default="in.xml", dest="in_file")
parser.add_argument("-p", action="store", type=str, dest="project")
parser.add_argument('--ducks', action='store_true', default=False, dest="process_ducks")
args = parser.parse_args()
print args.type
print args.project
if(args.type=="ClassIR"):
    sys.argv = ["main.py",args.project]
    runner = ClassIRRunner([args.project],args.process_ducks)
elif(args.type=="PotentialSiblings"):
    runner = PotentialSiblingsCounter([args.in_file])
elif(args.type=="VisualHierarchy"):
    runner = ClassHierarchyVisualizer([args.in_file])
elif(args.type=="FieldCandidates"):
    runner = FieldCandidateFinder([args.in_file])
elif(args.type=="LogilabObjectTracer"):
    sys.argv = ["main.py",args.project]
    runner = LogilabObjectTracer([args.project,args.in_file])
else:
    print "Unknown type!"
