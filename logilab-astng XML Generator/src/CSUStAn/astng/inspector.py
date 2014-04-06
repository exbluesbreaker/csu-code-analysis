'''
Created on 16.02.2013

@author: bluesbreaker
'''

from logilab.astng.inspector import Linker
from logilab import astng
from logilab.astng.inference import YES
from logilab.astng.utils import LocalsVisitor
from logilab.astng.inspector import IdGeneratorMixIn
from logilab.astng.scoped_nodes import *
from logilab.astng.node_classes import *
from pylint.pyreverse.utils import get_visibility
from CSUStAn.cross.duck_typing import DuckTypeHandler

class NoInferLinker(Linker):
    """ 
    
        Linker realization with no type inference
        
    """
    def __init__(self, project, inherited_interfaces=0, tag=False):
        Linker.__init__(self,project,inherited_interfaces,tag)
      
              
    def visit_assname(self, node):
        # avoid double parsing done by different Linkers.visit
        # running over the same project:
        if hasattr(node, '_handled'):
            return
        node._handled = True
        if node.name in node.frame():
            frame = node.frame()
        else:
            # the name has been defined as 'global' in the frame and belongs
            # there. Btw the frame is not yet visited as the name is in the 
            # root locals; the frame hence has no locals_type attribute
            frame = node.root()
        try:
            frame.locals_type[node.name] = [YES]
        except AttributeError:
            frame.locals_type ={node.name : [YES]}

    
    def handle_assattr_type(self, node, parent):
        parent.instance_attrs_type[node.attrname] = [YES]  
        
class DuckLinker(LocalsVisitor):
    
    _ducks_count = 0
    _linker = None
    _classes = []
    
    def __init__(self):
        LocalsVisitor.__init__(self)
    
    def handle_getattr_local(self,node,ducks,save_calls=False):
        ''' Handle Getattr node during duck typing for local names access 
            ducks - dictionary of processed ducks 
            save_calls flag for saving related to method ASTNG calls'''
        if(node.expr.as_string()!="self"):
            if not isinstance(node.expr, Getattr):
                ''' Handle duck typing for function/method arguments '''
                if not ducks.has_key(node.expr.as_string()):
                    if(save_calls):
                        ducks[node.expr.as_string()]={'attrs':set([]),'methods':{}}
                    else:
                        ducks[node.expr.as_string()]={'attrs':set([]),'methods':set([])}
                if isinstance(node.parent, CallFunc):
                    node.parent.g = '==><=='
                    if(save_calls):
                        if(ducks[node.expr.as_string()]['methods'].has_key(node.attrname)):
                            ducks[node.expr.as_string()]['methods'][node.attrname].add(node.parent)
                        else:
                            ducks[node.expr.as_string()]['methods'][node.attrname]=set([node.parent])
                    else:
                        ducks[node.expr.as_string()]['methods'].add(node.attrname)
                else:
                    ducks[node.expr.as_string()]['attrs'].add(node.attrname)
                        
    def handle_getattr_self(self,node,ducks):
        ''' Handle Getattr node during duck typing for "self"  names access 
            ducks - dictionary of processed ducks '''
        if((node.expr.as_string()=="self") and (get_visibility(node.attrname)!= 'special')):
            if isinstance(node.parent, For):
                if(not ducks.has_key(node.attrname)):
                    self._ducks_count +=1
                    ducks[node.attrname] = {'attrs':{},'methods':{},'type':[],'complex_type':'Unknown','assigned':False}
                    if isinstance(node.parent.target, AssName):
                        for body in node.parent.body:
                            self._check_cycle(body, node.parent.target.name, node.attrname, ducks)
            if isinstance(node.parent, Getattr):
                """ if additional info about attr's field may be obtained """
                if(not ducks.has_key(node.attrname)):
                    self._ducks_count += 1
                    ducks[node.attrname] = {'attrs':{}, 'methods':{}, 'type':[], 'complex_type':None, 'assigned':False}
                if isinstance(node.parent.parent, CallFunc):
                    """ we get info about attr's method """
                    self.add_duck_info(ducks[node.attrname],node.parent.attrname,'methods')
                else:
                    """ we get info about attr's attr """
                    self.add_duck_info(ducks[node.attrname],node.parent.attrname,'attrs')
            elif isinstance(node.parent, Subscript):
                """ attr of complex type (list, dict, tuple etc.) """
                if(not ducks.has_key(node.attrname)):
                    self._ducks_count +=1
                    ducks[node.attrname] = {'attrs':{},'methods':{},'type':[],'complex_type':'Unknown','assigned':False}
                else:
                    ducks[node.attrname]['complex_type'] = 'Unknown'
                if(isinstance(node.parent.parent,Getattr)):
                    """ get some info about element of complex type """
                    if(not ducks[node.attrname].has_key('element_signature')):
                        ducks[node.attrname]['element_signature']={'attrs':{},'methods':{}}
                    if isinstance(node.parent.parent.parent,CallFunc):
                        self.add_duck_info(ducks[node.attrname]['element_signature'],node.parent.parent.attrname,'methods')
                    else:
                        self.add_duck_info(ducks[node.attrname]['element_signature'],node.parent.parent.attrname,'attrs')
        
    def _check_cycle(self,node,iter_name,attr,ducks):
            """ Check body of cycle, which iterating over class's field"""
            if isinstance(node, Getattr):
                if(node.expr.as_string()==iter_name):
                    if(not ducks[attr].has_key('element_signature')):
                        ducks[attr]['element_signature']={'attrs':{},'methods':{}}
                    if isinstance(node.parent,CallFunc):
                        self.add_duck_info(ducks[attr]['element_signature'],node.attrname,'methods')
                    else:
                        self.add_duck_info(ducks[attr]['element_signature'],node.attrname,'attrs')
            for child in node.get_children():
                self._check_cycle(child,iter_name,attr,ducks)
                
    def handle_assattr_self(self,node,ducks):
        if((node.expr.as_string()=="self") and (get_visibility(node.attrname)!= 'special')):
            if(not ducks.has_key(node.attrname)):
                self._ducks_count +=1
                self._assigned_ducks +=1
                ducks[node.attrname] = {'attrs':{},'methods':{},'type':[],'complex_type':None,'assigned':True} 
            else:
                if(not ducks[node.attrname]['assigned']):
                    ducks[node.attrname]['assigned'] = True
                    self._assigned_ducks+=1
            if(isinstance(node.parent, (Assign,AugAssign))):
                if(isinstance(node.parent.value, (Tuple,Dict,List))):
                    ducks[node.attrname]['complex_type'] = node.parent.value.__class__.__name__ 
    
    def handle_assattr_local(self,node,ducks):
        pass
    
    def visit_class(self,node):
        self._classes.append(node)
        node.ucr_attrs = set([item[0] for item in node.items() if (isinstance(item[1], AssName) and (get_visibility(item[0])!= 'special'))])
        node.ucr_complete_attrs = node.ucr_attrs.copy()
    
    def leave_project(self,node):
        for cl in self.get_classes():
            map(lambda x: cl.ucr_complete_attrs.update(x.ucr_attrs), self.get_all_parents(cl))
            
    def handle_attrs(self,node,class_node):
        if class_node is None:
            return
        if isinstance(node, (AssAttr,Getattr)):
            if((node.expr.as_string()=="self") and (get_visibility(node.attrname)!= 'special')):
                class_node.ucr_attrs.add(node.attrname)
                
    def get_all_parents(self,class_node):
        for p in class_node.ancestors(recurs=True):
            if p in self._classes:
                yield p

class ClassIRLinker(IdGeneratorMixIn, DuckLinker):
    _num_attrs = 0
    _inherit = []
    _assigned_ducks = 0
    _processed_methods = 0
    _duck_handler = None
    
    def __init__(self, project):
        IdGeneratorMixIn.__init__(self)
        DuckLinker.__init__(self)
        self._duck_handler = DuckTypeHandler()
        
    def visit_class(self, node):
        node.cir_uid = self.generate_id()
        DuckLinker.visit_class(self, node)
        node.cir_methods = set([]) 
        node.cir_parents = set([])
        node.cir_ducks = {}
        for parent in node.ancestors(recurs=False):
            self._inherit.append((node,parent))
        
    def leave_class(self, node):
        self._num_attrs += len(node.ucr_attrs)
        
    def leave_project(self, node):
        """ delete non-project parents """
        for spec in self._inherit[:]:
            if not (spec[1] in self._classes):
                self._inherit.remove(spec)
            else:
                spec[0].cir_parents.add(spec[1])
        """ add complete class signatures """
        DuckLinker.leave_project(self, node)
        
    def visit_function(self, node):
        node.duck_info = {}
        if(node.args.args is not None):
            for arg in node.args.args:
                if not arg.name == 'self':
                    node.duck_info[arg.name]={'attrs':set([]),'methods':set([])}
        if isinstance(node.parent,Class):
            self._processed_methods +=1
            self.handle_attrs(node,node.parent)
            node.parent.cir_methods.add(node.name)  
        
    def add_duck_info(self,duck,name,label):
        if not duck[label].has_key(name):
            duck[label][name] = 1
        else:
            duck[label][name] += 1
    
    def handle_attrs(self,node,class_node):
        """ generate attrs and handle duck info about this attrs """
        DuckLinker.handle_attrs(self, node, class_node)
        if isinstance(node, (AssAttr,Getattr)):
            if isinstance(node, Getattr):
                self.handle_getattr_local(node, node.frame().duck_info)
                self.handle_getattr_self(node, class_node.cir_ducks)
            elif isinstance(node, AssAttr):
                self.handle_assattr_self(node, class_node.cir_ducks)    	
        for child in node.get_children():
            # Ignoring handling nested functions, it will be handled in another visit
            if not isinstance(child, (Function,Lambda,Class)):
                self.handle_attrs(child,class_node)
    
    def get_classes(self):
        for cl in self._classes:
            yield cl
    
    def get_ducks(self):
        for cl in self._classes:
            for duck in cl.cir_ducks.keys():
                yield cl.cir_ducks[duck]
    
    def get_methods(self,class_node):
        for it in class_node.items():
            if(isinstance(it[1], Function)):
                yield it[1]
                
    def get_inheritances(self):
        for inh in self._inherit:
            yield inh
                
    def get_complex_ducks(self):
        for cl in self._classes:
            for duck in cl.cir_ducks.keys():
                if cl.cir_ducks[duck]['complex_type']:
                    yield duck
    
    def get_assigned_ducks(self):
        for cl in self._classes:
            for duck in cl.cir_ducks.keys():
                if cl.cir_ducks[duck]['assigned']:
                    yield duck
                    
    def get_empty_ducks(self):
        for cl in self._classes:
            for duck in cl.cir_ducks.keys():
                if cl.cir_ducks[duck]['complex_type']:
                    if not cl.cir_ducks[duck].has_key('element_signature'):
                        yield duck
                    elif((not cl.cir_ducks[duck]['element_signature']['methods']) 
                        and 
                        (not cl.cir_ducks[duck]['element_signature']['attrs'])):
                        yield duck
                else:
                    if((not cl.cir_ducks[duck]['methods']) 
                        and 
                        (not cl.cir_ducks[duck]['attrs'])):
                        yield duck
                
    def get_ducks_count(self):
    	return self._ducks_count
    
    def get_attrs_count(self):
    	return self._num_attrs
