'''
Created on 16.02.2013

@author: bluesbreaker
'''

from logilab.astng.inspector import Linker
from logilab import astng
from logilab.astng.inference import YES

class NoInferLinker(Linker):
    """ 
    
        Linker realization with no type inference
        
    """
    _count =0
    def __init__(self, project, inherited_interfaces=0, tag=False):
         Linker.__init__(self,project,inherited_interfaces,tag)
    
    
    #def visit_assname(self, node):
     #   pass
        #self._count +=1
        #print self._count
    
    #def handle_assattr_type(self, node, parent):
     #   pass
        #print "ZZ"
        
    def visit_assname(self, node):
        """visit an astng.AssName node

        handle locals_type
        """
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
        frame.locals_type[node.name] = [YES]
    
    def handle_assattr_type(self, node, parent):
        parent.instance_attrs_type[node.attrname] = [YES]       