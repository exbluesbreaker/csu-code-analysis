'''
Created on 14.04.2013

@author: bluesbreaker
'''
from logilab.astng.utils import LocalsVisitor
from logilab.astng.inspector import IdGeneratorMixIn
from logilab.astng.node_classes import If
import pydot

class CFGLinker(IdGeneratorMixIn, LocalsVisitor):
    '''
    classdocs
    '''
    _stop=False

    def __init__(self, project):
        IdGeneratorMixIn.__init__(self)
        LocalsVisitor.__init__(self)
    def visit_function(self,node):
        if(self._stop or (len(list(node.get_children()))<4)):
            return
        graph = pydot.Dot(graph_type='digraph')
        self.extract(node,graph,0)
        #children = list(node.get_children())
        #blocks = [pydot.Node(child.__class__.__name__+' '+str(num),shape='record')for num,child in enumerate(children)]
        graph.write_svg('cfg.svg')
        f=open('cfg.txt','w')
        f.write(node.as_string())
        f.close()
        
    def extract(self,node,graph,id_count,parent=None):
        prev=parent
        if_prev = None
        for child in node.get_children():
            id_count+=1
            block = pydot.Node(child.__class__.__name__+' '+str(id_count),shape='record')
            graph.add_node(block)
            if prev is None:
                prev=block
            else:
                edge = pydot.Edge(prev,block)
                graph.add_edge(edge)
                prev=block
            if if_prev is not None:
                edge = pydot.Edge(if_prev,block)
                graph.add_edge(edge)
            if isinstance(child, If):
                self._stop = True
                id_count, if_prev = self.extract(child, graph, id_count, block)
            else:
                if_prev = None
        return id_count, block
                
       
        