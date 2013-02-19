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
    
    def __init__(self, project):
        IdGeneratorMixIn.__init__(self)
        LocalsVisitor.__init__(self)
        
    def visit_class(self, node):
        self._classes.append(node)
        node.uid = self.generate_id()
        node.attrs=set([item[0] for item in node.items() if (isinstance(item[1], AssName) and (get_visibility(item[0])!= 'special'))])
        for parent in node.ancestors(recurs=False):
            self._inherit.append((node,parent))
        
    def leave_class(self, node):
        self._num_attrs += len(node.attrs)
        
    def leave_project(self, node):
        # delete non-project parents
        for spec in self._inherit[:]:
            if not (spec[1] in self._classes):
                self._inherit.remove(spec)
        print self._num_attrs
        print len(self._inherit)
        
    def visit_function(self, node):
        if isinstance(node.parent,Class):
            self.get_attrs(node,node.parent)          
        pass
    
    def get_attrs(self,node,class_node):
        if isinstance(node, (AssAttr,Getattr)):
            if((node.expr.as_string()=="self") and (get_visibility(node.attrname)!= 'special')):
                class_node.attrs.add(node.attrname)
        for child in node.get_children():
            self.get_attrs(child,class_node)
