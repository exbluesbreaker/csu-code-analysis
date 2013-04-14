'''
Created on 14.04.2013

@author: bluesbreaker
'''
from logilab.astng.utils import LocalsVisitor
from logilab.astng.inspector import IdGeneratorMixIn
from logilab.astng.node_classes import If, For, While
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
        graph.write_svg('cfg.svg')
        f=open('cfg.txt','w')
        f.write(node.as_string())
        f.close()
        
    def extract(self,node,graph,id_count,parent=None):
        prev=parent
        if_prev = None
        for child in node.body:
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
                ''' merge of flows after if '''
                edge = pydot.Edge(if_prev,block)
                graph.add_edge(edge)
            if isinstance(child, If):
                test = pydot.Node(child.test.__class__.__name__+' '+str(id_count))
                graph.add_node(test)
                edge = pydot.Edge(block,test,dir='none',style='dashed')
                graph.add_edge(edge)
                id_count, if_prev = self.extract(child, graph, id_count, block)
            elif isinstance(child, (For, While)):
                if isinstance(child, For):
                    iterate = pydot.Node(child.iter.__class__.__name__+' '+str(id_count))
                    graph.add_node(iterate)
                    edge = pydot.Edge(block,iterate,dir='none',style='dashed')
                    graph.add_edge(edge)
                else:
                    self._stop = True
                    test = pydot.Node(child.test.__class__.__name__+' '+str(id_count))
                    graph.add_node(test)
                    edge = pydot.Edge(block,test,dir='none',style='dashed')
                    graph.add_edge(edge)
                id_count, cycle_prev = self.extract(child, graph, id_count, block)
                ''' cycle edge '''
                edge = pydot.Edge(cycle_prev,block)
                graph.add_edge(edge)
            else:
                if_prev = None
        return id_count, block
                
       
        