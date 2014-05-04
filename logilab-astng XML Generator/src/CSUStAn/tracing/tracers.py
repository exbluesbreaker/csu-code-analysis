'''
Created on 02.03.2014

@author: bluesbreaker
'''
import os
from logilab.astng.node_classes import *
from CSUStAn.tracing.class_tracer import CSUDbg
from CSUStAn.ucr.handling import TypesComparator

class ObjectTracer(TypesComparator):
    def __init__(self, project_tag, in_file, preload_file, skip_classes=(), delay=5,only_preload=False):
        TypesComparator.__init__(self, in_file,project_tag,preload_file)
        self._dbg = CSUDbg(project_mark=project_tag, skip_classes=skip_classes, delay=delay,preload_dt_info=self._preload_dt_info)
        self._dbg.set_trace()
        curr_dir = os.getcwd()
        if not only_preload:
            try:
                self.run()
            except SystemExit:
                """ Catching sys.exit """
                pass
        os.chdir(curr_dir)
        self._dbg.disable_trace()
        used_classes = self._dbg.get_used_classes()
        self._dynamic_types_info = used_classes
        t=0.1
        while t <=1.0:
            self.compare_type_info(threshold=t)
            print len(self._dynamic_types_info.keys()), self.get_num_of_classes()
            res =  self.get_result()
            print "Threshold - ", t
            print "Correctly detected common types: ",res['correct_common_types']
            print "Correctly detected aggregated types: ",res['correct_aggr_types']
            print "Not correctly detected common types: ",res['not_found_common_types']
            print "Not correctly detected aggregated types: ",res['not_found_aggr_types']
            print "Success percentage: ",(res['correct_common_types']+res['correct_aggr_types'])*100.0/(res['correct_common_types']+res['correct_aggr_types']+res['not_found_common_types']+res['not_found_aggr_types']),"%"
            t += 0.05
                        

class LogilabObjectTracer(ObjectTracer):
    
    def __init__(self, in_file, preload_file,only_preload=False):
        ObjectTracer.__init__(self,'logilab', in_file ,preload_file,skip_classes=(Const),only_preload=only_preload)
        
    def run(self):
        from pylint import run_pyreverse
        run_pyreverse()
#         from pylint.pyreverse import main
#         main.Run(sys.argv[1:])

class TwistedObjectTracer(ObjectTracer):
    
    def __init__(self, in_file,preload_file):
        ObjectTracer.__init__(self,'twisted', in_file ,preload_file)
        
    def run(self):
        twisted_ftpclient.run()
        
class PylintObjectTracer(ObjectTracer):
    
    def __init__(self, in_file, preload_file,only_preload=False):
        ObjectTracer.__init__(self,'pylint', in_file ,preload_file,skip_classes=(Const),only_preload=only_preload)
        
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
    
    def __init__(self, in_file, preload_file,work_dir,only_preload=False):
        import sys
        sys.setrecursionlimit(10000)
        from bzrlib.lazy_regex import LazyRegex
        self._work_dir = work_dir
        ObjectTracer.__init__(self,'bzrlib', in_file ,preload_file, skip_classes=(LazyRegex), delay=20,only_preload=only_preload)
        
    def run(self):
        os.chdir(self._work_dir)
        import bzrlib
        library_state = bzrlib.initialize()
        library_state.__enter__()
        try:
            exit_val = bzrlib.commands.main()
        finally:
            library_state.__exit__(None, None, None)
