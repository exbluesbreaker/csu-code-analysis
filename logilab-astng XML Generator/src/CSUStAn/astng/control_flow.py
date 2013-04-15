'''
Created on 14.04.2013

@author: bluesbreaker
'''
from logilab.astng.utils import LocalsVisitor
from logilab.astng.inspector import IdGeneratorMixIn
from logilab.astng.node_classes import If, For, While
import pydot
from lxml import etree

class CFGLinker(IdGeneratorMixIn, LocalsVisitor):
    '''
    classdocs
    '''
    _root = None
    ''' dbg '''
    _stop = False
    _stack = {}

    def __init__(self, project):
        IdGeneratorMixIn.__init__(self)
        LocalsVisitor.__init__(self)
    
    def visit_project(self,node):
        self._root = etree.Element("Project")
    def leave_project(self,node):
        f = open('cfg.xml','w')
        f.write(etree.tostring(self._root, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
    def visit_function(self,node):
        func_node = etree.Element("Function",name=node.name,label=node.root().name)
        self._stack[node] = func_node
        self._root.append(func_node)
        self.extract(node,func_node,0)
    def leave_function(self,node):
        ''' DEBUG '''
        if self._stop or (len(node.body)<4):
            del self._stack[node]
            return
        graph = pydot.Dot(graph_type='digraph')
        block_dict = {}
        for block in self._stack[node].iter("Block"):
            dot_node = pydot.Node(block.get("type")+' '+block.get("id"),shape='record')
            graph.add_node(dot_node)
            block_dict[block.get("id")] = dot_node
        for block in self._stack[node].iter("If"):
            dot_node = pydot.Node('If '+block.get("id")+'\l'+block.get("test"),shape='diamond')
            graph.add_node(dot_node)
            block_dict[block.get("id")] = dot_node
        for block in self._stack[node].iter("For"):
            dot_node = pydot.Node('For '+block.get("id")+'\l'+block.get("iterate"),shape='diamond')
            graph.add_node(dot_node)
            block_dict[block.get("id")] = dot_node
        for block in self._stack[node].iter("While"):
            dot_node = pydot.Node('While '+block.get("id")+'\l'+block.get("test"),shape='diamond')
            graph.add_node(dot_node)
            block_dict[block.get("id")] = dot_node
        for flow in self._stack[node].iter("Flow"):
            dot_edge = pydot.Edge(block_dict[flow.get("from_id")],block_dict[flow.get("to_id")])
            graph.add_edge(dot_edge)
        graph.write_svg('cfg.svg')
        f=open('cfg.txt','w')
        f.write(node.as_string())
        f.close()
        self._stop = True
        del self._stack[node]
        
    def extract(self,node,parent_node,id_count):
        prev=id_count
        if_prev = None
        for child in node.body:
            id_count+=1
            if isinstance(child, If):
                block_node = etree.Element("If",id=str(id_count))
            elif isinstance(child, For):
                block_node = etree.Element("For",id=str(id_count))
            elif isinstance(child, While):
                block_node = etree.Element("While",id=str(id_count))
            else:
                block_node = etree.Element("Block",type=child.__class__.__name__,id=str(id_count))
            curr_id = id_count
            parent_node.append(block_node)
            if prev == 0:
                prev=id_count
            else:
                flow_node = etree.Element("Flow",from_id=str(prev),to_id=str(curr_id))
                parent_node.append(flow_node)
                prev=id_count
            if if_prev is not None:
                ''' merge of flows after if '''
                flow_node = etree.Element("Flow",from_id=str(if_prev),to_id=str(curr_id))
                parent_node.append(flow_node)
                if_prev = None
            if isinstance(child, If):
                block_node.set("test",child.test.__class__.__name__)
                id_count = self.extract(child, parent_node, id_count)
                if_prev = id_count
            elif isinstance(child, (For, While)):
                if isinstance(child, For):
                    block_node.set("iterate",child.iter.__class__.__name__)
                else:
                    block_node.set("test",child.test.__class__.__name__)
                id_count = self.extract(child,parent_node, id_count)
                cycle_prev = id_count
                ''' cycle edge '''
                flow_node = etree.Element("Flow",from_id=str(cycle_prev),to_id=str(curr_id))
                parent_node.append(flow_node)
        return id_count
                
       
        