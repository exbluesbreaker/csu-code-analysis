'''
Created on 01.05.2012

@author: bluesbreaker
'''
import sys
import pydot
from operator import itemgetter
from pylint.pyreverse import main

trace_file = None
graph = pydot.Dot(graph_type='digraph')
dot_nodes = {}
dot_edges = {}
no_more_edges = False

def trace_calls(frame, event, arg):
    if event != 'call':
        return
    co = frame.f_code
    func_name = co.co_name
    trace_file.write(func_name+'\n')
    return 

def trace_modules(frame, event, arg):
    '''Trace calls between modules, and generate dot graph'''
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
    
    if((caller != called) and not no_more_edges):
        if(not dot_edges.has_key((caller,called))):
            dot_edges[(caller,called)] = 1
        else:
            dot_edges[(caller,called)] +=1
    return 

    


if __name__ == '__main__':
    #trace_file = open('trace.log','w')
    sys.settrace(trace_modules)
    main.Run(sys.argv[1:])
    # for multi-threading
    no_more_edges = True
    calls = []
    for call in dot_edges:
        calls.append((dot_edges[(call[0],call[1])],call[0],call[1]))
    #sorting key - count 
    calls = sorted(calls,key=itemgetter(0))
    num = 0
    for cluster in range(1,8):
        bound = calls[len(calls)*cluster/7-1]
        while((num < len(calls)) and (calls[num]<=bound)):
            edge = pydot.Edge(calls[num][1], 
                              calls[num][2], 
                              label=str(calls[num][0]), 
                              penwidth=str(cluster),arrowsize=str(1+cluster*1.0/7))
            graph.add_edge(edge)
            num+=1

    graph.write_png('test.png')
    #trace_file.close()