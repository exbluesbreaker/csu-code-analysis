'''
Created on 16.02.2013

@author: bluesbreaker
'''

from logilab.astng.inspector import Linker

class NoInferLinker(Linker):
    """ Linker realization with no type inference"""
    def __init__(self, project, inherited_interfaces=0, tag=False):
         Linker.__init__(self,project,inherited_interfaces,tag)
    
    
    def visit_assname(self, node):
        pass