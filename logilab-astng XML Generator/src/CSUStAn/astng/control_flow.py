'''
Created on 14.04.2013

@author: bluesbreaker
'''
from logilab.astng.utils import LocalsVisitor
from logilab.astng.inspector import IdGeneratorMixIn
from logilab.astng.node_classes import If, For, While, TryExcept, TryFinally, IfExp, With,\
    CallFunc
from logilab.astng.scoped_nodes import Class, Function
import pydot
from lxml import etree

JUMP_NODES = ( If, For, While, TryExcept, TryFinally, IfExp, With)

class CFGLinker(IdGeneratorMixIn, LocalsVisitor):
    '''
    classdocs
    '''
    _root = None
    ''' dbg '''
    _stop = False
    _stack = {}
    _dbg = False
    _dbg1 = None

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
        if isinstance(node.parent,Class):
            func_node = etree.Element("Method",name=node.name,parent_class=node.parent.name,label=node.root().name)
        else:
            func_node = etree.Element("Function",name=node.name,label=node.root().name)
        self._stack[node] = func_node
        self._root.append(func_node)
        id_count, prev = self.handle_flow_part(func_node,node.body, set([]),0)
        id_count +=1
        block_node = etree.Element("Block", type="<<Exit>>",id=str(id_count))
        func_node.append(block_node)
        for p in prev:
            flow_node = etree.Element("Flow",from_id=str(p),to_id=str(id_count))
            func_node.append(flow_node)
    def leave_function(self,node):
        ''' DEBUG '''
        if self._stop:
            del self._stack[node]
            return
        if not (self._dbg == True):
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
        del self._stack[node]
        self._stop = True
        
    def handle_flow_part(self,func_node,flow_part, parent_ids,id_count):
        ''' Handle sequential part of flow, e.g then or else body of If'''
        prev=parent_ids
	block_node = None
	#block_node = etree.Element("Block",id=str(id_count))
	#func_node.append(block_node)
        for child in flow_part:
            if isinstance(child, Function):
                ''' Ignore function defined in another function body'''
                continue
            id_count+=1
            '''if isinstance(child, If):
                subblock_node = etree.Element("If",id=str(id_count))
            elif isinstance(child, For):
                subblock_node = etree.Element("For",id=str(id_count))
            elif isinstance(child, While):
                subblock_node = etree.Element("While",id=str(id_count))
            else:
                subblock_node = etree.Element("SubBlock",type=child.__class__.__name__,id=str(id_count))'''
            curr_id = id_count
            #block_node.append(subblock_node)
	    if(isinstance(child,(If,While,For,TryExcept,TryFinally,With)) or (block_node is None)):
	    	for p in prev:
                	flow_node = etree.Element("Flow",from_id=str(p),to_id=str(curr_id))
                	func_node.append(flow_node)
            if isinstance(child, If):
		if_node = etree.Element("If",id=str(id_count),test=child.test.__class__.__name__)
		func_node.append(if_node)
                id_count, prev = self.handle_cross(child,func_node, curr_id, id_count)
		block_node = None
            elif isinstance(child, For):
		for_node = etree.Element("For",id=str(id_count),iterate=child.iter.__class__.__name__)
		func_node.append(for_node)
                id_count, prev = self.handle_cross(child,func_node, curr_id, id_count)
		block_node = None
            elif isinstance(child, While):
		while_node = etree.Element("While",id=str(id_count),test=child.test.__class__.__name__)
		func_node.append(while_node)
                id_count, prev = self.handle_cross(child,func_node, curr_id, id_count)
		block_node = None
            elif isinstance(child, (TryExcept,TryFinally,With)):
		jump_node = etree.Element(child.__class__.__name__,id=str(id_count))
		func_node.append(jump_node)
                id_count, prev = self.handle_cross(child,func_node, curr_id, id_count)
		block_node = None
            else:
                #self.handle_simple_node(child)
		if block_node is None:
		   block_node = etree.Element("Block",id=str(id_count))
		   func_node.append(block_node)
		   prev = set([id_count])
		   id_count+=1
		   subblock_node = etree.Element("SubBlock",type=child.__class__.__name__,id=str(id_count))
		   block_node.append(subblock_node)
	        else:
		   subblock_node = etree.Element("SubBlock",type=child.__class__.__name__,id=str(id_count))
		   block_node.append(subblock_node)
        return id_count, prev
    
    def handle_cross(self, node, func_node, parent_id,id_count):
        ''' Handle conditional part of flow, e.g. If block'''
        curr_id = id_count
        parent_ids = set([]) 
        if isinstance(node, (If,While, For)):
            id_count, ids = self.handle_flow_part(func_node,node.body, set([curr_id]), id_count)
            parent_ids |=ids
            id_count, ids = self.handle_flow_part(func_node,node.orelse, set([curr_id]), id_count)
            parent_ids |=ids
            parent_ids.add(curr_id)
        elif isinstance(node, TryExcept):
             id_count, ids = self.handle_flow_part(func_node,node.body, set([curr_id]), id_count)
             parent_ids |=ids
             for h in node.handlers:
                 id_count, ids = self.handle_flow_part(func_node,h.body, set([curr_id]), id_count)
                 parent_ids |=ids
             id_count, ids = self.handle_flow_part(func_node,node.orelse, set([curr_id]), id_count)
             parent_ids |=ids
             parent_ids.add(curr_id)
        elif isinstance(node, TryFinally):
             id_count, ids = self.handle_flow_part(func_node,node.body, set([curr_id]), id_count)
             parent_ids |=ids
             id_count, ids = self.handle_flow_part(func_node,node.finalbody, set([curr_id]), id_count)
             parent_ids |=ids
             parent_ids.add(curr_id)
        elif isinstance(node, With):
             id_count, ids = self.handle_flow_part(func_node,node.body, set([curr_id]), id_count)
             parent_ids |=ids
             parent_ids.add(curr_id)
        return id_count, parent_ids            
    
    def handle_simple_node(self, node):
        if isinstance(node, JUMP_NODES):
            print "Warning! Ignored jump node at ", node.root
            self._dbg = True
        elif isinstance(node, CallFunc):
            print node.as_string(),node.func
            print node.scope().lookup(node.func)
        for child in node.get_children():
            self.handle_simple_node(child)
       
        
