'''
Created on 20.05.2014

@author: bluesbreaker
'''

def graph_connected_components(adj_map):
    ''' Return list of connected components contents for given graph, specified with adjacency map'''
    def dfs(node,adj_map,usd_map,component_contents):
        component_contents.append(node)
        usd_map[node] = True
        for sub_node in adj_map[node]:
            if(not usd_map[sub_node]):
                dfs(sub_node,adj_map,usd_map,component_contents)
        return component_contents
    connected_components = []
    usd_map = {}
    for node in adj_map.keys():
        usd_map[node] = False
    for node in adj_map.keys():
        if(not usd_map[node]):
            connected_components.append(dfs(node,adj_map,usd_map,[]))
    return connected_components 