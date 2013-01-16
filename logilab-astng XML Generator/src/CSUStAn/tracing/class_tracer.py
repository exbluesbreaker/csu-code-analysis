'''
Created on 08.01.2013

@author: bluesbreaker
'''
import sys
from bdb import Bdb
import inspect
from operator import itemgetter
from pylint.pyreverse import main
from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import *
from sets import Set

class CSUDbg(Bdb):
    _project_mark = None
    _used_classes_dict = {}
    _project_classes = 0
    _non_project_classes = 0
    _no_more_trace = False
    def __init__(self, project_mark, skip=None):
        Bdb.__init__(self, skip=skip)
        self._project_mark = project_mark
    def trace_dispatch(self,frame, event, arg):
        if(self._no_more_trace):
            return
        for  var in frame.f_locals:
            obj = frame.f_locals[var]
            if not (inspect.isbuiltin(obj) or inspect.isclass(obj)):
                #print inspect.getfile(frame.f_locals[var])
                if self._handle_obj(obj):
                    self._project_classes += 1
                    full_name = inspect.getmodule(obj).__name__+'.'+obj.__class__.__name__
                    if not self._used_classes_dict.has_key(full_name): 
                        self._used_classes_dict[full_name] = 1
                    else:
                        self._used_classes_dict[full_name] += 1
                    if not isinstance(obj, Const):
                        inspect.getmembers(obj)
                    #for attr in inspect.getmembers(obj):
                    #    sub_obj = attr[1]
                    #    if not (inspect.isbuiltin(sub_obj) or inspect.isclass(sub_obj)):
                    #        if self._handle_obj(sub_obj):
                    #            print "Gotcha!"
                else:
                    self._non_project_classes += 1
                #if isinstance(frame.f_locals[var], NodeNG):
                #    print frame.f_locals[var]
        #print "I debugging it!"
    def get_used_classes(self):
        return self._used_classes_dict.copy()
    def get_classes_usage(self):
        return {"Project classes":self._project_classes, "Non-project classes":self._non_project_classes}
    def get_most_popular_classes(self):
        pass
    def _handle_obj(self,obj):
        module = inspect.getmodule(obj)
        if module:
            if(module.__name__.find(self._project_mark)!=-1):
                return True
        return False 
    def disable_trace(self):
        self._no_more_trace = True
        

trace_file = None
dot_nodes = {}
dot_edges = {}
no_more_trace = False

test_var = 3

def test_func(str1):
    a = 4
    print str1

def trace_calls(frame, event, arg):
    if event != 'call':
        return
    co = frame.f_code
    func_name = co.co_name
    trace_file.write(func_name+'\n')
    return 

def trace_modules(frame, event, arg):
    '''Trace calls between modules, and generate dot graph'''
    global current_module
    #print "++++++++++++++++++++++++"
    #print frame.f_back, frame.f_builtins, frame.f_code, frame.f_exc_traceback, frame.f_exc_type, frame.f_exc_value, frame.f_globals, frame.f_lasti, frame.f_lineno, frame.f_locals, frame.f_restricted, frame.f_trace
    #print  frame.f_globals
    #print "------------------------"  
    #print  frame.f_locals  
    #print frame.f_globals, frame.f_locals
    for  var in frame.f_locals:
        try:
            if isinstance(var, NodeNG):
                print var
        except TypeError:
            continue
    if event != 'call':
        return
     

    


if __name__ == '__main__':
    #trace_file = open('trace.log','w')
    #sys.settrace(trace_modules)
    dbg = CSUDbg(project_mark='logilab')
    test = CallFunc()
    dbg.set_trace()
    #test_func("Arg")
    #main.Run(sys.argv[1:])
    # for multi-threading
    no_more_trace = True
    used_classes = dbg.get_used_classes()
    for key, value in sorted(used_classes.iteritems(), key=lambda (k,v): (v,k)):
        print "%s: %s" % (key, value)
    print len(used_classes.keys())
    print dbg.get_classes_usage()