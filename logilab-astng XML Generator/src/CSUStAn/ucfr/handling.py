'''
Created on 02.03.2014

@author: bluesbreaker
'''
from lxml import etree
from logilab.astng.inspector import IdGeneratorMixIn
from CSUStAn.exceptions import CSUStAnException

class UCFRHandler:
    ''' Process UCFR XML '''
    _cfg_tree = None
    _methods = None
    _funcs = None
    #_full_name_dict = None
    #_id_dict = None
    def __init__(self, cfg_xml):
        parser = etree.XMLParser(remove_blank_text=True)
        self._cfg_tree = etree.parse(cfg_xml, parser)
        self._methods = [node for node in self._cfg_tree.iter("Method")]
        self._funcs = [node for node in self._cfg_tree.iter("Function")]
        
    def get_frame_by_id(self,id):
        return self._cfg_tree.xpath("//Method[@cfg_id=\""+id+"\"]|Function[@cfg_id=\""+id+"\"]")
    
    def get_targeted_calls(self):
        return self._cfg_tree.xpath("//Target[@cfg_id]")
    
    def get_frames(self):
        return self._cfg_tree.xpath("//Method|Function")
    
    def get_calls(self,frame):
        pass
    
    def for_each_method(self, function):
        for method in self._methods:
            function(method)
            
    def get_num_of_methods(self):
        return len(self._methods)
    
class UCFRSlicer(UCFRHandler):
    ''' Abstract UCFR-slicer '''
    _out_xml = None
    _sliced_frames = None
    
    def __init__(self,lcfg_xml,out_xml):
        UCFRHandler.__init__(self, lcfg_xml)
        self._out_xml = out_xml
        
    
    def slice(self):
        self.extract_slicing()
        ''' Extract sliced methods/funcs from CFG'''
        for frame in self._cfg_tree.xpath("//Method|//Function"):
            if frame not in self._sliced_frames:
                frame.getparent().remove(frame)
        f = open(self._out_xml,'w')
        f.write(etree.tostring(self._cfg_tree, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
            
class FlatUCFRSlicer(UCFRSlicer):
    _id = None
    _criteria = None
    _visited = set([])
    
    def __init__(self,lcfg_xml,out_xml,target_id,criteria):
        UCFRSlicer.__init__(self, lcfg_xml,out_xml)
        self._id = target_id
        self._criteria = criteria
        self.slice()
        
    def extract_slicing(self):
        if self._criteria == "callers":
            self.handle_callers()
        elif self._criteria == "tree":
            self.handle_tree()
        else:
            print "Unknown CFG slicing criteria!"
            return
        print len(self._sliced_frames),"methods after slicing"
    
    def handle_tree(self,node_id=None):
        ''' Slice methods/funcs called from given'''
        if node_id is None:
            self._sliced_frames = set([])
            node_id = self._id
        if node_id in self._visited:
            return
        self._visited.add(node_id)
        self._sliced_frames|=set(self._cfg_tree.xpath("//Function[@cfg_id=\""+node_id+"\"]|//Method[@cfg_id=\""+node_id+"\"]"))
        calls = self._cfg_tree.xpath("//Method[@cfg_id=\""+node_id+"\"]//Target[@cfg_id]|\
                                                        //Function[@cfg_id=\""+node_id+"\"]//Target[@cfg_id]")
        for id in set([c.get("cfg_id") for c in calls]):
            self.handle_tree(id)
            
    def handle_callers(self):
        ''' Slice callers methods/funcs for given'''
        ''' method/func of interest'''
        self._sliced_frames=set(self._cfg_tree.xpath("//Function[@cfg_id=\""+self._id+"\"]|//Method[@cfg_id=\""+self._id+"\"]"))
        ''' calls of method/func of interest'''
        for call in self._cfg_tree.xpath("//Target[@cfg_id=\""+self._id+"\"]"):
            self._sliced_frames.add(call.getparent().getparent().getparent().getparent())
            
class ClassUCFRSlicer(UCFRSlicer):
    ''' Slice methods-creators of given class '''
    _ucr_id = None
    _criteria = None  
    
    def __init__(self, lcfg_xml, out_xml, target_id, criteria):
        UCFRSlicer.__init__(self, lcfg_xml, out_xml)
        self._ucr_id = target_id
        self._criteria = criteria
        self.slice()
    
    def extract_slicing(self):
        if self._criteria == "creators":
            self.handle_creators()
        elif self._criteria == "created":
            self.handle_created()
        else:
            print "Unknown CFG slicing criteria!"
            return
        print len(self._sliced_frames), "methods after slicing"
        
        
    def handle_creators(self):
        ''' Slice method/funcs,which created given class'''
        self._sliced_frames = set([])
        ''' calls of method/func of interest'''
        for call in self._cfg_tree.xpath("//TargetClass[@ucr_id=\"" + self._ucr_id + "\"]"):
            if call.getparent().getparent().tag=='Direct':
                self._sliced_frames.add(call.getparent().getparent().getparent().getparent().getparent())
                
                
class ExecPathHandler(UCFRHandler,IdGeneratorMixIn):
    
    def __init__(self,lcfg_xml):
        UCFRHandler.__init__(self, lcfg_xml)
        IdGeneratorMixIn.__init__(self)
    
    def get_call_route(self,block_path,call):
        call_path=[]
        for b in block_path[:-1]:
            for c in b.iter("Call"):
                call_path.append(c)
        for c in block_path[-1].iter("Call"):
            call_path.append(c)
            if(c.xpath(".//Target[@cfg_id=\""+call+"\"]")):
                break
        return call_path
            
    def extract_frame_path(self,frame_node,block_node):
        ''' Extract all possible paths from frame start to given block '''
        flows = frame_node.xpath(".//Flow[@to_id=\'"+block_node.get("id")+"\']")
        # local_path |= set(flows)
        local_path = []
        if len(flows)==0:
            return[[block_node]]
        for f in flows:
            precending = frame_node.xpath(".//*[@id=\'"+f.get("from_id")+"\']")
            paths = self.extract_frame_path(frame_node, precending[0])
            #print paths
            for p in paths:
                p.append(block_node)
            local_path = local_path+paths
        return local_path
    
    def extract_frame_routes(self,exec_path):
        '''Extract all possible global frame routes for given path'''
        curr_frame_calls = self.get_call_targets(exec_path[0])
        frame = self.get_frame_by_id(exec_path[0])[0]
        frame_routes = []
        frame_names = [frame.get("label")+'.'+frame.get("name")]
        for f in exec_path[1:]:
            target_calls=[c for c in curr_frame_calls if c.get("cfg_id")==f]
            if len(target_calls)==0:
                raise CSUStAnException("No such exec path"+str(exec_path)+". Failed on "+str(f))
            for c in target_calls:
                block = c.xpath("./ancestor::Block")[0]
                frame_routes.append(self.extract_frame_path(frame, block)) 
            curr_frame_calls = self.get_call_targets(f)
            frame = self.get_frame_by_id(f)[0]
            frame_names.append(frame.get("label")+'.'+frame.get("name"))
        result_routes = [[f] for  f in frame_routes[0]]
        for r in frame_routes[1:]:
            result_routes = self.concat_routes(result_routes, r)  
        return frame_names, result_routes      
    
    def get_call_targets(self,frame_id):
        nodes =  self.get_frame_by_id(frame_id)
        if(len(nodes)>1):
            print "Warning: multiple nodes for exec path entry id(",frame_id,")"
        if(len(nodes)==0):
            raise CSUStAnException("Error: No nodes for exec path entry id("+str(frame_id)+")")
            return None
        return nodes[0].xpath(".//Target[@cfg_id]")
