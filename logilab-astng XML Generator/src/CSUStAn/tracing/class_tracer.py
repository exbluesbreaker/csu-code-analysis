'''
Created on 08.01.2013

@author: bluesbreaker
'''
import sys
from bdb import Bdb
import inspect
import pdb
from operator import itemgetter
from pylint.pyreverse import main
from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import *
from sets import Set

class CSUDbg(Bdb):
    _project_mark = None
    _used_classes_dict = None
    _project_classes = 0
    _non_project_classes = 0
    _no_more_trace = False
    def __init__(self, project_mark, skip=None):
        Bdb.__init__(self, skip=skip)
        self._project_mark = project_mark
        self._used_classes_dict = {}
    def trace_dispatch(self,frame, event, arg):
        if(self._no_more_trace):
            return
        for  var in frame.f_locals:
            obj = frame.f_locals[var]
            if self._handle_obj(obj):
                    self._project_classes += 1
                    full_name = inspect.getmodule(obj).__name__+'.'+obj.__class__.__name__
                    if not self._used_classes_dict.has_key(full_name): 
                        self._used_classes_dict[full_name] = [1,{}]
                    else:
                        self._used_classes_dict[full_name][0] += 1
                    if not isinstance(obj, Const):
                        #inspect.getmembers(obj)
                        #dir(obj)
                        for attr in inspect.getmembers(obj):
                            sub_obj = attr[1]
                            complex_type = self._check_complex_attr(sub_obj)
                            if complex_type is not None:
                                #add complex type info
                                if not self._used_classes_dict[full_name][1].has_key(attr[0]):
                                    self._used_classes_dict[full_name][1][attr[0]] = {'common_type':Set([]),'aggregated_type':Set([complex_type])}
                                else:
                                    self._used_classes_dict[full_name][1][attr[0]]['aggregated_type'].add(complex_type)
                                pass 
                            elif self._handle_obj(sub_obj):
                                    #add common type info
                                    if not self._used_classes_dict[full_name][1].has_key(attr[0]):
                                        self._used_classes_dict[full_name][1][attr[0]] = {'common_type':Set([inspect.getmodule(sub_obj).__name__+'.'+sub_obj.__class__.__name__]),'aggregated_type':Set([])}
                                    else:
                                        self._used_classes_dict[full_name][1][attr[0]]['common_type'].add(inspect.getmodule(sub_obj).__name__+'.'+sub_obj.__class__.__name__)
            else:
                    self._non_project_classes += 1
    def _check_complex_attr(self,obj):
        if type(obj) in(list,tuple):
            if(len(obj)>0):
                if self._handle_obj(obj[0]):
                    return inspect.getmodule(obj[0]).__name__+'.'+obj[0].__class__.__name__
        if type(obj) is dict:
            dict_keys = obj.keys()
            if(len(dict_keys)>0):
                if self._handle_obj(obj[dict_keys[0]]):
                    return inspect.getmodule(obj[dict_keys[0]]).__name__+'.'+obj[dict_keys[0]].__class__.__name__
        return None
    def get_used_classes(self):
        return self._used_classes_dict.copy()
    def get_classes_usage(self):
        return {"Project classes":self._project_classes, "Non-project classes":self._non_project_classes}
    def get_most_popular_classes(self):
        pass
    def _handle_obj(self,obj):
        if (inspect.ismethod(obj) or inspect.isclass(obj) or inspect.istraceback(obj) or inspect.isbuiltin(obj) or inspect.ismodule(obj) or inspect.isfunction(obj)):
            return False
        module = inspect.getmodule(obj)
        if module:
            if(module.__name__.find(self._project_mark)!=-1):
                return True
        return False 
    def disable_trace(self):
        self._no_more_trace = True
        

project_mark = 'logilab'
used_classes_dict = {}
project_classes = 0
non_project_classes = 0
trace_file = None
dot_nodes = {}
dot_edges = {}
no_more_trace = False
test_var = 3

def handle_obj(obj):
        module = inspect.getmodule(obj)
        if module:
            if(module.__name__.find(project_mark)!=-1):
                return True
        return False 

def test_func(str1):
    a = 4
    print str1

def trace_logilab(frame, event, arg):
    global used_classes_dict, project_classes, non_project_classes
    if(no_more_trace):
            return
    for  var in frame.f_locals:
        obj = frame.f_locals[var]
        if not (inspect.isbuiltin(obj) or inspect.isclass(obj)):
            if handle_obj(obj):
                project_classes += 1
                full_name = inspect.getmodule(obj).__name__+'.'+obj.__class__.__name__
                if not used_classes_dict.has_key(full_name): 
                    used_classes_dict[full_name] = 1
                else:
                    used_classes_dict[full_name] += 1
                if not isinstance(obj, Const):
                    inspect.getmembers(obj)
                        #dir(obj)
                    #for attr in inspect.getmembers(obj):
                    #    sub_obj = attr[1]
                    #    if not (inspect.isbuiltin(sub_obj) or inspect.isclass(sub_obj)):
                    #        if self._handle_obj(sub_obj):
                    #            print "Gotcha!"
                else:
                    non_project_classes += 1

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
    sys.settrace(trace_logilab)
    #dbg = CSUDbg(project_mark='logilab')
    test = CallFunc()
    #dbg.set_trace()
    #test_func("Arg")
    main.Run(sys.argv[1:])
    # for multi-threading
    no_more_trace = True
    used_classes = used_classes_dict
    for key, value in sorted(used_classes.iteritems(), key=lambda (k,v): (v,k)):
        print "%s: %s" % (key, value)
    print len(used_classes.keys())