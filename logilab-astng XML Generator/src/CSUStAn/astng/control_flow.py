'''
Created on 14.04.2013

@author: bluesbreaker
'''
from logilab.astng.utils import LocalsVisitor
from logilab.astng.inspector import IdGeneratorMixIn
from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import Class, Function, Lambda
from logilab.astng.exceptions import InferenceError
from CSUStAn.astng.inspector import DuckLinker
import pydot
import re 
from lxml import etree

JUMP_NODES = ( If, For, While, TryExcept, TryFinally, IfExp, With)

class UCFRLinker(IdGeneratorMixIn, DuckLinker):
    '''
    classdocs
    '''
    _root = None
    ''' dbg '''
    _stop = False
    _stack = {}
    _dbg = False
    _dbg1 = None
    _project_name = None
    _dbg_calls = set([])
    _dbg_call_lookup = set([])
    _getattr_calls = 0
    _func_calls = 0
    _class_calls = 0
    _out_xml = None
    _ids = set([])
    _frames = set([])
    ''' Map of ASTNG calls to UCFR calls '''
    _call_dict = {}
    '''DEBUG'''
    dbg = 0

    def __init__(self, project_name, out_xml):
        IdGeneratorMixIn.__init__(self)
        DuckLinker.__init__(self)
        self._project_name = project_name
        self._out_xml = out_xml
    
    def visit_project(self,node):
        self._root = etree.Element("Project",name=self._project_name)
              
    def write_result(self,node):
        print self._dbg_calls
        print self._dbg_call_lookup
        all_calls = self._func_calls+self._class_calls+self._getattr_calls
        print "Func calls ",self._func_calls,self._func_calls*100.0/all_calls,"%"
        print "Class calls ",self._class_calls,self._class_calls*100.0/all_calls,"%"
        print "Getattr calls ",self._getattr_calls,self._getattr_calls*100.0/all_calls,"%"
        for t in self._root.xpath("//Target[@cfg_id]"):
            if not int(t.get("cfg_id")) in self._ids:
                t.attrib.pop("cfg_id")
        f = open(self._out_xml,'w')
        f.write(etree.tostring(self._root, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
    
    def handle_id(self,func_node):
        if isinstance(func_node.parent,Class):
            if not hasattr(func_node, "id"):
                func_node.id = self.generate_id()
            func_node.visited=True
            return func_node.id
        else:
            if hasattr(func_node.root(),'func_dict'):
                func_node.root.func_dict = {}
            if not func_node.root.func_dict.has_key(func_node.name):
                func_node.root.func_dict[func_node.name] =self.generate_id()
            return func_node.root.func_dict[func_node.name]   
    
    def visit_class(self,node):
        DuckLinker.visit_class(self, node)
        
    def get_frames(self):
        return self._frames
    
    def get_classes(self):
        return self._classes
    
    def visit_function(self,node):
        self.dbg += 1
        self._frames.add(node)
        func_id = self.handle_id(node)
        self._ids.add(func_id)
        if(len(node.body)>8):
            self._dbg = True
        if isinstance(node.parent,Class):
            func_node = etree.Element("Method",cfg_id=str(func_id),name=node.name,parent_class=node.parent.name,label=node.root().name)
            class_node = node.parent
        else:
            func_node = etree.Element("Function",cfg_id=str(func_id),name=node.name,label=node.root().name)
            class_node = None
        self._stack[node] = func_node
        self._root.append(func_node)
        returns = set([])
        ''' extract duck typing '''
        node.duck_info = {}
        if(node.args.args is not None):
            for arg in node.args.args:
                if not arg.name == 'self':
                    node.duck_info[arg.name]={'attrs':set([]),'methods':{}}
        self.extract_duck_types(node,class_node)
        id_count, prev = self.handle_flow_part(func_node,node.body, set([]),0,returns)
        id_count +=1
        block_node = etree.Element("Block", type="<<Exit>>",id=str(id_count))
        func_node.append(block_node)
        ''' Flows to the end of function '''
        for p in prev.union(returns):
            flow_node = etree.Element("Flow",from_id=str(p),to_id=str(id_count))
            func_node.append(flow_node)
            
    def extract_duck_types(self,node,class_node):
        """ generate attrs and handle duck info about this attrs """
        DuckLinker.handle_attrs(self, node, class_node)
        if isinstance(node, (AssAttr,Getattr)):
            if isinstance(node, Getattr):
                self.handle_getattr_local(node, node.frame().duck_info,True)
            elif isinstance(node, AssAttr):
                self.handle_assattr_local(node, node.frame().duck_info)   
            ''' Handle only 1 level Getattr-s'''
            return     
        for child in node.get_children():
            # Ignoring handling nested functions, it will be handled in another visit
            if not isinstance(child, (Function,Lambda,Class)):
                self.extract_duck_types(child,class_node)
        
    def leave_function(self,node):
        return
        ''' DEBUG '''
        if self._stop:
            del self._stack[node]
            return
        if not (self._dbg == True):
            return
        graph = pydot.Dot(graph_type='digraph')
        block_dict = {}
        for block in self._stack[node].iter("Block"):
            dot_node = pydot.Node(block.get("id"),shape='record')
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
        
    def leave_project(self, node):
        """ add complete class signatures """
        DuckLinker.leave_project(self, node)
        
    def handle_flow_part(self,func_node,flow_part, parent_ids,id_count,returns):
        ''' Handle sequential object of flow, e.g then or else body of If'''
        prev=parent_ids
        block_node = None
        for child in flow_part:
            if isinstance(child, Function):
                ''' Ignore function defined in another function body'''
                continue
            id_count+=1
            curr_id = id_count
            #block_node.append(subblock_node)
            if(isinstance(child, (If, While, For, TryExcept, TryFinally, With)) or (block_node is None)):
                for p in prev:
                    if (p not in returns):
                        flow_node = etree.Element("Flow", from_id=str(p), to_id=str(curr_id))
                        func_node.append(flow_node)
            if isinstance(child, If):
                if_node = etree.Element("If", id=str(id_count), test=child.test.__class__.__name__)
                if_node.set("fromlineno",str(child.fromlineno))
                if_node.set("col_offset",str(child.col_offset))
                func_node.append(if_node)
                id_count, prev = self.handle_cross(child, func_node, curr_id, id_count,returns)
                block_node = None
            elif isinstance(child, For):
                for_node = etree.Element("For", id=str(id_count), iterate=child.iter.__class__.__name__)
                for_node.set("fromlineno",str(child.fromlineno))
                for_node.set("col_offset",str(child.col_offset))
                func_node.append(for_node)
                id_count, prev = self.handle_cross(child, func_node, curr_id, id_count,returns)
                block_node = None
            elif isinstance(child, While):
                while_node = etree.Element("While", id=str(id_count), test=child.test.__class__.__name__)
                while_node.set("fromlineno",str(child.fromlineno))
                while_node.set("col_offset",str(child.col_offset))
                func_node.append(while_node)
                id_count, prev = self.handle_cross(child, func_node, curr_id, id_count,returns)
                block_node = None
            elif isinstance(child, (TryExcept, TryFinally, With)):
                jump_node = etree.Element(child.__class__.__name__, id=str(id_count))
                jump_node.set("fromlineno",str(child.fromlineno))
                jump_node.set("col_offset",str(child.col_offset))
                func_node.append(jump_node)
                id_count, prev = self.handle_cross(child, func_node, curr_id, id_count,returns)
                block_node = None
            else:
                if block_node is None:
                    block_node = etree.Element("Block", id=str(id_count))
                    block_node.set("fromlineno",str(child.fromlineno))
                    block_node.set("col_offset",str(child.col_offset))
                    func_node.append(block_node)
                    prev = set([id_count])
                    if(isinstance(child, Return)):
                        returns.add(id_count)
                    id_count += 1
                self.handle_simple_node(child, block_node)
        if(flow_part):
            return id_count, prev
        else:
            return id_count, set([])
    
    def handle_cross(self, node, func_node, parent_id,id_count,returns):
        ''' Handle conditional part of flow, e.g. If block'''
        curr_id = id_count
        parent_ids = set([]) 
        if isinstance(node, If):
            id_count, ids = self.handle_flow_part(func_node,node.body, set([curr_id]), id_count,returns)
            parent_ids |=ids
            id_count, ids = self.handle_flow_part(func_node,node.orelse, set([curr_id]), id_count,returns)
            parent_ids |=ids
            if (not node.orelse):
                ''' If there are no else then no direct block from if is needed'''
                parent_ids.add(curr_id)
        elif isinstance(node, (While, For)):
            id_count, ids = self.handle_flow_part(func_node,node.body, set([curr_id]), id_count,returns)
            for p in ids:
                    if (p not in returns):
                        flow_node = etree.Element("Flow", from_id=str(p), to_id=str(curr_id))
                        func_node.append(flow_node)
            parent_ids.add(curr_id)
            if (not node.orelse):
                ''' If there are no else then no direct block from if is needed'''
                parent_ids.add(curr_id)
        elif isinstance(node, TryExcept):
            id_count, ids = self.handle_flow_part(func_node,node.body, set([curr_id]), id_count,returns)
            parent_ids |=ids
            for h in node.handlers:
                id_count, ids = self.handle_flow_part(func_node,h.body, set([curr_id]), id_count,returns)
                parent_ids |=ids
            id_count, ids = self.handle_flow_part(func_node,node.orelse, set([curr_id]), id_count,returns)
            parent_ids |=ids
        elif isinstance(node, TryFinally):
            id_count, ids = self.handle_flow_part(func_node,node.body, set([curr_id]), id_count,returns)
            parent_ids |=ids
            id_count, ids = self.handle_flow_part(func_node,node.finalbody, set([curr_id]), id_count,returns)
            parent_ids |=ids
        elif isinstance(node, With):
            id_count, ids = self.handle_flow_part(func_node,node.body, set([curr_id]), id_count,returns)
            parent_ids |=ids
        return id_count, parent_ids            
    
    def handle_simple_node(self,node,block_node):
        if isinstance(node, JUMP_NODES):
            print "Warning! Ignored jump node at ", node.root
            #self._dbg = True
        elif isinstance(node, CallFunc):
            call_node = etree.Element("Call")
            self._dbg_calls.add(node.func.__class__.__name__)
            call_node.set("fromlineno",str(node.fromlineno))
            call_node.set("col_offset",str(node.col_offset))
            if isinstance(node.func, Name):
                space_type,called,called_id, label = self.handle_lookup(node.func, node.func.name)
                if called == 'function':
                    self._func_calls += 1
                elif called == 'class':
                    self._class_calls += 1
                call_subnode = etree.Element("Direct",name=node.func.name)
                if space_type is not None:
                    call_subnode.set("space_type",space_type)
                target_subnode = etree.Element("Target")
                call_subnode.append(target_subnode)
                if called=='function':
                    target_subnode.set("type","function")
                    if label is not None:
                        target_subnode.set("label",label)
                elif called=='class':
                    target_subnode.set("type","method")
                    class_subnode = etree.Element("TargetClass")
                    if label is not None:
                        class_subnode.set("label",label)
                    target_subnode.append(class_subnode)
                else:
                    target_subnode.set("type","unknown")
                if called_id is not None:
                    target_subnode.set("cfg_id",str(called_id))
                call_node.append(call_subnode)
            elif isinstance(node.func, Getattr):
                self._getattr_calls += 1
                call_subnode = etree.Element("Getattr")
                call_subnode.set("name",node.func.attrname)
                call_subnode.set("label",node.func.expr.as_string())
                call_node.append(call_subnode)
            block_node.append(call_node)
            ''' save call for further access '''
            self._call_dict[node]=call_node
            #print node.as_string(),node.func
            #print node.scope().lookup(node.func)
        for child in node.get_children():
            self.handle_simple_node(child,block_node)
            
    def get_call(self,call):
        if self._call_dict.has_key(call):
            return self._call_dict[call]
        else:
            return None
    
    def handle_lookup(self,node,name,space_type=None):
        lookup = node.lookup(name)
        called = None
        called_id = None
        label = None
        for asgn in lookup[1]:
            if isinstance(asgn, Function):
                if(space_type is None):
                    space_type = "internal"
                called = "function"
                label = asgn.root().name
                if (label == '__builtin__') or (space_type == "external"):
                    ''' No id generation for non-project calls '''
                    continue 
                called_id = self.handle_id(asgn)
            elif isinstance(asgn, Class):
                if(space_type is None):
                    space_type = "internal"
                called = "class"
                label = asgn.root().name   
                if label == '__builtin__':
                    continue             
                for cstr in [meth for meth in asgn.methods() if ((re.split('\W+', meth.parent.root().name)[0] == self._project_name)and(meth.name == '__init__'))]:
                    called_id = self.handle_id(cstr)
            elif isinstance(asgn, From):
                try:
                    module = asgn.do_import_module(asgn.modname)
                    if((space_type is None) and (re.split('\W+', module.name)[0] == self._project_name)):
                        space_type = "cross"
                    else:
                        space_type = "external"
                    label = asgn.root().name
                    # Here is the situation when we have lib/builtin module with same name that in project.

                    # It imports correctly and causes infinite recursion.

                    if label == '__builtin__' and space_type == "external" and module.name == asgn.modname:
                        raise InferenceError(module.name)
                    if not module.name.startswith(self._project_name):
                        raise InferenceError(module.name)
                    space_type,called,called_id, label = self.handle_lookup(module, name, space_type)
                except InferenceError:
                    if(space_type is None):
                        space_type = "external"
            self._dbg_call_lookup.add(asgn.__class__.__name__)
            if isinstance(asgn,AssAttr):
                print "DBG ",name,asgn.as_string(), asgn.root()
        return space_type,called,called_id, label
