'''
Created on 02.03.2014

@author: bluesbreaker
'''

import pydot
from logilab.common.configuration import ConfigurationMixIn
from CSUStAn.ucr.handling import ClassIRHandler
from pylint.pyreverse.main import OPTIONS

class UCRVisualizer:
    ''' generate dot from UCR '''
    
    def visual_classes(self,classes,out_file):
        graph = pydot.Dot(graph_type='digraph')
        dot_classes = {} 
        #setup classes
        for node in classes:
            class_text = node.get("name")+"(ucr_id="+node.get("id")+")"
            attrs = [a for a in node.iter("Attr")]
            if(len(attrs)>0):
                class_text += "|Attrs|"
            for attr in attrs:
                class_text += attr.get("name")+"\l"
            methods = [m for m in node.iter("Method")]
            if(len(methods)>0):
                class_text += "|Methods|"
            for method in methods:
                class_text += method.get("name")+"\l"
            class_node = pydot.Node(node.get("id"),label="{"+class_text+"}",shape='record')
            dot_classes[node.get("id")] = class_node
            graph.add_node(class_node)
        #setup relations
        for node in classes:
            parents = [parent for parent in node.iter("Parent")]
            for parent in parents:
                edge = pydot.Edge(dot_classes[node.get("id")], dot_classes[parent.get("id")])
                graph.add_edge(edge)
        graph.write_svg(out_file)



class ClassHierarchyVisualizer(ConfigurationMixIn,ClassIRHandler,UCRVisualizer):
    ''' generate dot from XML UCR '''
    
    options = OPTIONS
    _out_file = None
    
    def __init__(self, in_file,out_file):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        ClassIRHandler.__init__(self, in_file)
        self._out_file = out_file
        self.run()
    
    def run(self):
        self.visual_classes(self._classes, self._out_file)
