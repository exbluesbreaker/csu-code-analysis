'''
Created on 02.03.2014

@author: bluesbreaker
'''

from CSUStAn.ucfr.visual import ExecRouteVisualizer
from CSUStAn.ucr.visual import UCRVisualizer
from CSUStAn.ucr.handling import UCRSlicer

class ExecPathObjectSlicer(ExecRouteVisualizer,UCRSlicer,UCRVisualizer):
    def __init__(self,lcfg_xml,ucr_xml,exec_path,out_dir='.'):
        ExecRouteVisualizer.__init__(self, lcfg_xml)
        UCRSlicer.__init__(self, ucr_xml)
        self._out_dir = out_dir
        frame_names, routes  = self.extract_frame_routes(exec_path)
        self.run(routes,frame_names,exec_path)
        
    def run(self,routes,frame_names,exec_path):
        i = 0
        for route in routes:
            created_classes=set([])
            for frame in route:
                for block in frame:
                    for target_class in block.xpath(".//Direct/Target/TargetClass"):
                        created_classes.add(target_class.get("ucr_id"))
            graph = self.dot_route(route, exec_path, frame_names)
            graph.write(self._out_dir+'/route_'+str(i)+'.dot')
            graph.write_svg(self._out_dir+'/route_'+str(i)+'.svg')
            self._cids = created_classes
            root_node = self.slice_ucr()
            self.write_slicing(self._out_dir+'/route_'+str(i)+'_objects.xml',root_node)
            self.visual_classes(root_node, self._out_dir+'/route_'+str(i)+'_objects.svg')
            i+=1
            #print created_classes
        self.visualize_frames(exec_path, self._out_dir)
    
    def slice(self):
        self._sliced_classes = set([])
        for c in self._cids:
            current_class = self.get_class_by_id(c)
            self._sliced_classes.add(current_class)
            parents = self.get_all_parents(current_class,None)
            for p in parents:
                self._sliced_classes.add(p)
