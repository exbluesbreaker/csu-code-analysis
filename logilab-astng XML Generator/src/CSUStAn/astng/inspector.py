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

class ClassIRLinker(IdGeneratorMixIn, LocalsVisitor):
    _num_attrs = 0
    _inherit = []
    _classes = []
    _ducks_count = 0
    _assigned_ducks = 0
    _processed_methods = 0
    
    def __init__(self, project):
        IdGeneratorMixIn.__init__(self)
        LocalsVisitor.__init__(self)
        
    def visit_class(self, node):
        self._classes.append(node)
        node.cir_uid = self.generate_id()
        node.cir_attrs = set([item[0] for item in node.items() if (isinstance(item[1], AssName) and (get_visibility(item[0])!= 'special'))])
        node.cir_parents = set([])
        node.cir_ducks = {}
        node.cir_complete_attrs = node.cir_attrs.copy()
        for parent in node.ancestors(recurs=False):
            self._inherit.append((node,parent))
        
    def leave_class(self, node):
        self._num_attrs += len(node.cir_attrs)
        
    def leave_project(self, node):
        """ delete non-project parents """
        for spec in self._inherit[:]:
            if not (spec[1] in self._classes):
                self._inherit.remove(spec)
            else:
                spec[0].cir_parents.add(spec[1])
        """ add complete class signatures """
        for cl in self._classes:
            map(lambda x: cl.cir_complete_attrs.update(x.cir_attrs), self.get_all_parents(cl))
        print "Processed methods ", self._processed_methods
        
    def visit_function(self, node):
        if isinstance(node.parent,Class):
        	self._processed_methods +=1
        	self.handle_attrs(node,node.parent)          
    
    
    def handle_attrs(self,node,class_node):
        """ ganerate attrs and handle duck info about this attrs """
        if isinstance(node, (AssAttr,Getattr)):
            if((node.expr.as_string()=="self") and (get_visibility(node.attrname)!= 'special')):
                class_node.cir_attrs.add(node.attrname)
            if isinstance(node, Getattr):
                if((node.expr.as_string()=="self") and (get_visibility(node.attrname)!= 'special')):
                    if isinstance(node.parent, For):
                        if(not class_node.cir_ducks.has_key(node.attrname)):
                            self._ducks_count +=1
                            class_node.cir_ducks[node.attrname] = {'attrs':set([]),'methods':set([]),'type':[],'complex_type':'Unknown','assigned':False}
                        if isinstance(node.parent.target, AssName):
                            for body in node.parent.body:
                                self._check_cycle(body, node.parent.target.name, node.attrname, class_node)
                    if isinstance(node.parent, Getattr):
                    	""" if additional info about attr's field may be obtained """
                    	if(not class_node.cir_ducks.has_key(node.attrname)):
                        	self._ducks_count += 1
                        	class_node.cir_ducks[node.attrname] = {'attrs':set([]), 'methods':set([]), 'type':[], 'complex_type':None, 'assigned':False}
                    	if isinstance(node.parent.parent, CallFunc):
                    		print class_node.cir_ducks[node.attrname]['methods']
                        	""" we get info about attr's method """
                        	class_node.cir_ducks[node.attrname]['methods'].add(node.parent.attrname)
                    	else:
                        	""" we get info about attr's attr """
                        	class_node.cir_ducks[node.attrname]['attrs'].add(node.parent.attrname)
                    elif isinstance(node.parent, Subscript):
                		""" attr of complex type (list, dict, tuple etc.) """
                		if(not class_node.cir_ducks.has_key(node.attrname)):
                			self._ducks_count +=1
                			class_node.cir_ducks[node.attrname] = {'attrs':set([]),'methods':set([]),'type':[],'complex_type':'Unknown','assigned':False}
                		else:
                			class_node.cir_ducks[node.attrname]['complex_type'] = 'Unknown'
                		if(isinstance(node.parent.parent,Getattr)):
                			# get some info about element of complex type
                			if(not class_node.cir_ducks[node.attrname].has_key('element_signature')):
                				class_node.cir_ducks[node.attrname]['element_signature']={'attrs':set([]),'methods':set([])}
                			if isinstance(node.parent.parent.parent,CallFunc):
                				class_node.cir_ducks[node.attrname]['element_signature']['methods'].add(node.parent.parent.attrname)
                			else:
                				class_node.cir_ducks[node.attrname]['element_signature']['attrs'].add(node.parent.parent.attrname)
            elif isinstance(node, AssAttr):
            	if((node.expr.as_string()=="self") and (get_visibility(node.attrname)!= 'special')):
            		if(not class_node.cir_ducks.has_key(node.attrname)):
            			self._ducks_count +=1
            			self._assigned_ducks +=1
            			class_node.cir_ducks[node.attrname] = {'attrs':set([]),'methods':set([]),'type':[],'complex_type':None,'assigned':True} 
            		else:
            			if(not class_node.cir_ducks[node.attrname]['assigned']):
            				class_node.cir_ducks[node.attrname]['assigned'] = True
            				self._assigned_ducks+=1
            		if(isinstance(node.parent, (Assign,AugAssign))):
            			if(isinstance(node.parent.value, (Tuple,Dict,List))):
            				class_node.cir_ducks[node.attrname]['complex_type'] = node.parent.value.__class__.__name__     	
        for child in node.get_children():
            self.handle_attrs(child,class_node)
    
    
    def _check_cycle(self,node,iter_name,attr,class_node):
        """ Check body of cycle, which iterating over class's field"""
        if isinstance(node, Getattr):
            if(node.expr.as_string()==iter_name):
                if(not class_node.cir_ducks[attr].has_key('element_signature')):
                    class_node.cir_ducks[attr]['element_signature']={'attrs':set([]),'methods':set([])} 
                if isinstance(node.parent,CallFunc):
                    class_node.cir_ducks[attr]['element_signature']['methods'].add(node.attrname)
                else:
                    class_node.cir_ducks[attr]['element_signature']['attrs'].add(node.attrname)           
        for child in node.get_children():
            self._check_cycle(child,iter_name,attr,class_node)   
    
    def get_classes(self):
        for cl in self._classes:
            yield cl
            
    def get_all_parents(self,class_node):
        for p in class_node.ancestors(recurs=True):
            if p in self._classes:
                yield p
                
    def get_ducks_count(self):
    	return self._ducks_count
    
    def get_attrs_count(self):
    	return self._num_attrs
