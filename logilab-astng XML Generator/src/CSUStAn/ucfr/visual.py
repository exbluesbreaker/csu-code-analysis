'''
Created on 02.03.2014

@author: bluesbreaker
'''
import os
import pydot
from CSUStAn.ucfr.handling import UCFRHandler
from CSUStAn.ucfr.handling import ExecPathHandler

class UCFRVisualizer(UCFRHandler):
    _out_dir = None
    def __init__(self,lcfg_xml,out_dir):
        UCFRHandler.__init__(self, lcfg_xml)
        self._out_dir = out_dir
        self.run()
    def run(self):
        for meth in self._cfg_tree.xpath("//Method"):
            self.handle_frame(meth)
        for func in self._cfg_tree.xpath("//Function"):
            self.handle_frame(func)
    def handle_frame(self,node):
        graph = pydot.Dot(graph_type='digraph',compound='true')
        block_dict = {}
        call_cnt = 0
        for block in node.iter("Block"):
            block_node = pydot.Cluster(block.get("id")+'_',shape='record',label='Block '+str(block.get("id")))
            dbg_cnt = call_cnt
            call_node = None
            for c in block.iter("Call"):
                call_color = 'black'
                call_url = '#'
                if((len(c.getchildren())>0) and (c.getchildren()[0].get("called")=='class')):
                    call_color = 'blue'
                elif((len(c.getchildren())>0) and (c.getchildren()[0].get("called")=='function')):
                    call_color = 'yellow'
                elif((len(c.getchildren())>0) and (c.getchildren()[0].tag=='Getattr')):
                    call_color = 'green'
                if (((len(c.getchildren())>0)) and('called_id'in c.getchildren()[0].keys())):
                    call_url = os.path.abspath(self._out_dir+'/'+c.getchildren()[0].get('called_id')+'.svg')
                    call_color = 'red'
                call_node = pydot.Node('Call '+str(dbg_cnt),shape='record',color=call_color,URL=call_url)
                dbg_cnt += 1
                block_node.add_node(call_node)
            if dbg_cnt == call_cnt:
                block_node = pydot.Node('Block '+str(block.get("id")),shape='record')
                graph.add_node(block_node)
                block_dict[block.get("id")] = block_node
            else:
                graph.add_subgraph(block_node)
                block_dict[block.get("id")] = (block_node,call_node)
                call_cnt = dbg_cnt
        for block in node.iter("If"):
            block_node = pydot.Node('If '+block.get("id"),shape='diamond')
            #block.get("test")
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for block in node.iter("For"):
            block_node = pydot.Node('For '+block.get("id"),shape='diamond')
            #block.get("iterate")
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for block in node.iter("While"):
            block_node = pydot.Node('While '+block.get("id"),shape='diamond')
            #block.get("test")
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for block in node.iter("TryExcept"):
            block_node = pydot.Node('TryExcept',shape='diamond')
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for block in node.iter("TryFinally"):
            block_node = pydot.Node('TryFinally',shape='diamond')
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for block in node.iter("With"):
            block_node = pydot.Node('With',shape='diamond')
            graph.add_node(block_node)
            block_dict[block.get("id")] = block_node
        for flow in node.iter("Flow"):
            from_node = block_dict[flow.get("from_id")]
            if isinstance(from_node,tuple):
                tail = from_node[1]
                tail_l = from_node[0]
            else:
                tail=from_node
                tail_l = None
            to_node = block_dict[flow.get("to_id")]
            if isinstance(to_node,tuple):
                head = to_node[1]
                head_l = to_node[0]
            else:
                head = to_node
                head_l = None
            if((tail_l is None) and (head_l is None)):
                dot_edge = pydot.Edge(tail,head)
            elif((tail_l is not None) and (head_l is None)):
                dot_edge = pydot.Edge(tail,head,ltail=tail_l.get_name())
            elif((tail_l is None) and (head_l is not None)):
                dot_edge = pydot.Edge(tail,head,lhead=head_l.get_name())
            else:
                dot_edge = pydot.Edge(tail,head,ltail=tail_l.get_name(),lhead=head_l.get_name())
            graph.add_edge(dot_edge)
        graph.write_svg(self._out_dir+'/'+node.get("cfg_id")+'.svg')
        
        
class ExecRouteVisualizer(ExecPathHandler):
    ''' Class for visualization of one exec route '''
    def __init__(self,lcfg_xml):
        ExecPathHandler.__init__(self, lcfg_xml)
        
    def dot_route(self,route,exec_path,frame_names):
        graph = pydot.Dot(graph_type='digraph',compound='true')
        prev = None
        for r,f,f_name in zip(route,exec_path[:-1],frame_names[:-1]):
            func_node = pydot.Cluster(str(self.generate_id()),shape='record',label=f_name+"(cfg_id="+f+")")
            blocks = []
            for b in r:
                block_node = self.dot_block(b)
                if isinstance(block_node, tuple):
                    func_node.add_subgraph(block_node[0])
                    blocks.append(block_node)
                else:
                    func_node.add_node(block_node)
                    blocks.append(block_node)
            route_edges = zip(blocks[:-1],blocks[1:])
            if prev is not None:
                route_edges.append((prev,blocks[0]))
            for from_node,to_node in route_edges:
                dot_edge = self.dot_flow_edge(from_node,to_node)
                graph.add_edge(dot_edge)
            graph.add_subgraph(func_node)
            prev = blocks[-1]
        last_func = pydot.Cluster(str(self.generate_id()),shape='record',label=frame_names[-1])
        graph.add_subgraph(last_func)
        last_node = pydot.Node(str(self.generate_id()),shape='record',label='Func '+exec_path[-1])
        dot_edge = pydot.Edge(prev[1],last_node,ltail=prev[0].get_name(),lhead=last_func.get_name())
        last_func.add_node(last_node)
        graph.add_edge(dot_edge)
        return graph
    
    def concat_routes(self,start_routes,end_routes):
        result = []
        for r0 in start_routes:
            for r1 in end_routes:
                r0.append(r1)
                result.append(r0)
        return result
    
    def dot_call(self,call_node):
        dot_id = self.generate_id()
        target = call_node.getchildren()[0]
        cfg_targets = call_node.xpath(".//Target[@cfg_id]")
        ucr_targets = call_node.xpath(".//Direct/Target/TargetClass")
        if len(cfg_targets)>0:
            cfg_target = "(cfg_id="+cfg_targets[0].get("cfg_id")+")"
        else:
            cfg_target = ""
        if (len(ucr_targets)>0) and (ucr_targets[0].get("ucr_id") is not None):
            ucr_target = "(ucr_id="+ucr_targets[0].get("ucr_id")+")"
        else:
            ucr_target = ""
        if(target.tag == "Getattr"):
            dot_call = pydot.Node(str(dot_id), label="\""+target.get("label") + '.' + target.get("name")+cfg_target+ucr_target+"\"", shape='record')
        else:
            dot_call = pydot.Node(str(dot_id), label="\""+target.get("name")+cfg_target+ucr_target+"\"", shape='record')
        return dot_call
    
    def dot_block(self,block):
        dot_id = self.generate_id()
        cond_blocks = ["If","While","For","With","TryExcept","TryFinally"]
        if block.tag in cond_blocks:
            block_node = pydot.Node(dot_id,label=block.tag,shape='diamond')
            return block_node
        call_nodes = [c for c in block.iter("Call")]
        if(len(call_nodes)>0):
            block_node = pydot.Cluster(str(dot_id),shape='record',label='Block '+str(block.get("id")))
            for c in call_nodes[:-1]:
                call_node = self.dot_call(c)
                block_node.add_node(call_node)
            call_node = self.dot_call(call_nodes[-1])
            block_node.add_node(call_node)
            return block_node,call_node
        else:
            block_node = pydot.Node(str(dot_id),shape='record',label='Block '+str(block.get("id")))
            return block_node
    
    def dot_flow_edge(self,from_node,to_node):
        if isinstance(from_node,tuple):
            tail = from_node[1]
            tail_l = from_node[0]
        else:
            tail=from_node
            tail_l = None
        if isinstance(to_node,tuple):
            head = to_node[1]
            head_l = to_node[0]
        else:
            head = to_node
            head_l = None
        if((tail_l is None) and (head_l is None)):
            dot_edge = pydot.Edge(tail,head)
        elif((tail_l is not None) and (head_l is None)):
            dot_edge = pydot.Edge(tail,head,ltail=tail_l.get_name())
        elif((tail_l is None) and (head_l is not None)):
            dot_edge = pydot.Edge(tail,head,lhead=head_l.get_name())
        else:
            dot_edge = pydot.Edge(tail,head,ltail=tail_l.get_name(),lhead=head_l.get_name())
        return dot_edge
    
    def visualize_frames(self,exec_path,out_dir):
        frames = [self.get_frame_by_id(f)[0] for f in exec_path]
        graph = pydot.Dot(graph_type='digraph',compound='true')
        for f in frames:
            frame_graph = pydot.Cluster(f.get("cfg_id"),shape='record',label=f.get("label")+'.'+f.get("name")+"(cfg_id="+f.get("cfg_id")+")")
            block_dict = {}
            for block in f.iter("Block"):
                block_node = self.dot_block(block)
                if isinstance(block_node, tuple):
                    frame_graph.add_subgraph(block_node[0])
                    block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
                else:
                    frame_graph.add_node(block_node)
                    block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("If"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("For"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("While"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("TryExcept"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("TryFinally"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for block in f.iter("With"):
                block_node = self.dot_block(block)
                frame_graph.add_node(block_node)
                block_dict[block.get("id")+'_'+f.get("cfg_id")] = block_node
            for flow in f.iter("Flow"):
                from_node = block_dict[flow.get("from_id")+'_'+f.get("cfg_id")]
                to_node = block_dict[flow.get("to_id")+'_'+f.get("cfg_id")]
                dot_edge = self.dot_flow_edge(from_node, to_node)
                frame_graph.add_edge(dot_edge)
            graph.add_subgraph(frame_graph)
        graph.write(out_dir+'/frames.dot')
        graph.write_svg(out_dir+'/frames.svg')
    
class ExecPathVisualizer(ExecRouteVisualizer):
    ''' Visualizer for all routes of given exec path, also functions from CFG will be visualized '''
       
    def __init__(self,lcfg_xml,exec_path,out_dir='.'):
        ExecRouteVisualizer.__init__(self, lcfg_xml)
        self._out_dir = out_dir   
        self.visualize_frames(exec_path,out_dir)
        self.visualize_exec_path(exec_path)
        
    def visualize_exec_path(self,exec_path):
        '''Visualize all possible routes for given exec path '''
        frame_names, result_routes = self.extract_frame_routes(exec_path)
        i=0
        for route in result_routes:
            graph = self.dot_route(route,exec_path,frame_names)
            graph.write(self._out_dir+'/route'+str(i)+'.dot')
            graph.write_svg(self._out_dir+'/route'+str(i)+'.svg')
            i+=1