'''
Created on 01.05.2012

@author: bluesbreaker
'''
import sys
import pydot
from pylint.pyreverse import main

trace_file = None
graph = pydot.Dot(graph_type='digraph')
dot_nodes = {}
dot_edges = {}

def trace_calls(frame, event, arg):
    if event != 'call':
        return
    co = frame.f_code
    func_name = co.co_name
    trace_file.write(func_name+'\n')
    return 

def trace_modules(frame, event, arg):
    global current_module
    caller = frame.f_back.f_code.co_filename
    called = frame.f_code.co_filename
    if event != 'call':
        return
    if(not dot_nodes.has_key(caller)):
        dot_nodes[caller] = pydot.Node(caller, shape='record')
        graph.add_node(dot_nodes[caller])
    if(not dot_nodes.has_key(called)):
        dot_nodes[called] = pydot.Node(called, shape='record')
        graph.add_node(dot_nodes[called])
    if(caller != called):
        if(not dot_edges.has_key((caller,called))):
            graph.add_edge(pydot.Edge(dot_nodes[caller],dot_nodes[called]))
            dot_edges[(caller,called)] = 'true'
    return 

    


if __name__ == '__main__':
    #trace_file = open('trace.log','w')
    sys.settrace(trace_modules)
    main.Run(sys.argv[1:])
    graph.write_png('test.png')
    #trace_file.close()