'''
Created on 02.03.2014

@author: bluesbreaker
'''

import numpy
from lxml import etree
from CSUStAn.ucfr.handling import UCFRHandler
from CSUStAn.ucr.handling import ClassIRHandler,UCRSlicer
from CSUStAn.exceptions import CSUStAnException

class DataflowLinker(UCFRHandler,ClassIRHandler):
    _targeted = 0
    _out_xml = None
    _typed_ga_calls = 0
    _unknown_ga_calls = 0
    _class_dict = {}
    _input_ucr = None
    _input_ucfr = None
    def __init__(self,ucr_xml,cfg_xml,out_xml):
        ClassIRHandler.__init__(self, ucr_xml)
        UCFRHandler.__init__(self, cfg_xml)
        self._input_ucr = ucr_xml
        self._input_ucfr = cfg_xml
        self._out_xml = out_xml
        self.run()
    def run(self):
        self.link_methods(self._cfg_tree)
    def link_methods(self,xml_node):
        for meth in self._cfg_tree.xpath("//Method"):
            parent_class = self.get_class_by_full_name(meth.get("label")+'.'+meth.get("parent_class"))
            meth.set("ucr_id",parent_class.get("id"))
            self._class_dict[parent_class.get("id")+meth.get("name")]=meth
        for call in self._cfg_tree.xpath("//TargetClass"):
            target_class = self.get_class_by_full_name(call.get("label")+'.'+call.getparent().getparent().get("name"))
            if(not target_class is None):
                call.set("ucr_id",target_class.get("id"))
        for call in self._cfg_tree.xpath("//Getattr[starts-with(@label,\"self.\")]"):
            frame = call.getparent().getparent().getparent()
            if(frame.tag=='Method'):
                source_class = self.get_class_by_full_name(frame.get("label")+'.'+frame.get("parent_class"))
                attr = self.get_attr(source_class,call.get("label")[5:])
                if(attr is not None):
                    attr_types = list(attr.iter("CommonType"))
                    if(len(attr_types)>0):
                        self._typed_ga_calls +=1
                    else:
                        self._unknown_ga_calls +=1
                        target_node = etree.Element("Target",type="unknown")
                        call.append(target_node)
                    for t in attr_types:
                        if self._class_dict.has_key(t.get("id")+call.get("name")):
                            meth = self._class_dict[t.get("id")+call.get("name")]
                            tgt_node = etree.Element("Target",type="method", cfg_id=meth.get("cfg_id"))
                            call.append(tgt_node)
                        else:
                            tgt_node = etree.Element("Target",type="method")
                            call.append(tgt_node)
                        tgt_class_node = etree.Element("TargetClass", ucr_id=t.get("id"))
                        tgt_node.append(tgt_class_node)
        f = open(self._out_xml,'w')
        f.write(etree.tostring(self._cfg_tree, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
        print "Processed",self._input_ucr, "and",self._input_ucfr
        print "Written",self._out_xml  

class InstanceInitSlicer(UCFRHandler, UCRSlicer):
    ''' Search for all classes, created in methods of given class '''
    _ucr_id = None
    _keep_parents = None
    _criteria = None
    _input_ucr_xml = None
    _input_ucfr_xml = None
    def __init__(self,ucr_xml,lcfg_xml,ucr_id,out_xml,keep_parents=False,criteria='creators'):
        UCRSlicer.__init__(self, ucr_xml)
        UCFRHandler.__init__(self, lcfg_xml)
        self._input_ucr_xml = ucr_xml
        self._input_ucfr_xml = lcfg_xml
        self._ucr_id = ucr_id
        self._keep_parents = keep_parents
        self._criteria = criteria
        root_node = self.slice_ucr()
        self.write_slicing(out_xml,root_node)
        
        
    def slice(self):
        if self._criteria == 'creators':
            self.slice_creators()
        elif self._criteria == 'created':
            self.slice_created()
        elif self._criteria == 'summary':
            self.handle_summary()
        else:
            raise CSUStAnException("Unknown criteria - "+self._criteria+"!")
        
    def handle_summary(self):
        init_dict = {c.get("id"):[] for c in self._classes}
        for c in self._cfg_tree.xpath("//Method//Direct//Target[@type=\"method\"]//TargetClass[@ucr_id]"):
            creator = c.getparent().getparent().getparent().getparent().getparent()
            init_dict[creator.get("ucr_id")].append(c.get("ucr_id"))
            print "Method",creator.get("name")+"[cfg_id="+creator.get("cfg_id")+"] of",creator.get("parent_class")+"[ucr_id="+creator.get("ucr_id")+"] creates object of class",c.getparent().getparent().get("name")+"[ucr_id="+c.get("ucr_id")+"]"
        unique_init_dict = {c:set(init_dict[c])for c in init_dict.keys()}
        inits = [len(init_dict[c]) for c in init_dict.keys()]
        unique_inits = [len(init_dict[c]) for c in unique_init_dict.keys()]
        print "Processed",self._input_ucr_xml,"and",self._input_ucfr_xml
        print "Max objects inits for class", numpy.max(inits)
        print "Avg objects inits for class", numpy.average(inits)
        print "Standard deviation objects inits for class", numpy.std(inits)
                
    def slice_creators(self):
        current_class = self.get_class_by_id(self._ucr_id)
        self._sliced_classes.add(current_class)
        parents = None
        if(self._keep_parents):
                parents = self.get_all_parents(current_class,parents)
        else:
            for p in current_class.iter("Parent"):
                    current_class.remove(p)
        for c in self._cfg_tree.xpath("//Method[@ucr_id=\""+self._ucr_id+"\"]//Direct//Target[@type=\"method\"]//TargetClass[@ucr_id]"):
            created_class = self.get_class_by_id(c.get("ucr_id")) 
            self._sliced_classes.add(created_class)
            if(self._keep_parents):
                parents = self.get_all_parents(created_class,parents)
            else:
                for p in created_class.iter("Parent"):
                    created_class.remove(p)
        if parents is not None:
            for p in parents:
                self._sliced_classes.add(p)
    def slice_created(self):
        current_class = self.get_class_by_id(self._ucr_id)
        self._sliced_classes.add(current_class)
        parents = None
        if(self._keep_parents):
                parents = self.get_all_parents(current_class,parents)
        else:
            for p in current_class.iter("Parent"):
                    current_class.remove(p)
        for c in self._cfg_tree.xpath("//Method//Direct//Target[@type=\"method\"]//TargetClass[@ucr_id=\""+self._ucr_id+"\"]"):
            creator_class = self.get_class_by_id(c.getparent().getparent().getparent().getparent().getparent().get("ucr_id")) 
            self._sliced_classes.add(creator_class)
            if(self._keep_parents):
                parents = self.get_all_parents(creator_class,parents)
            else:
                for p in creator_class.iter("Parent"):
                    creator_class.remove(p)
        if parents is not None:
            for p in parents:
                self._sliced_classes.add(p)
                
class UnreachableCodeSearch(UCFRHandler, ClassIRHandler):
    _ucr_id = None
    _keep_parents = None
    _call_map = {}
    def __init__(self,ucr_xml,lcfg_xml):
        ClassIRHandler.__init__(self, ucr_xml)
        UCFRHandler.__init__(self, lcfg_xml)
        self.get_call_map()
        all_frames = set([f.get("cfg_id") for f in self.get_frames()])
        all_called = set(self._call_map.keys())
        not_called = all_frames-all_called
        not_called_frames = set([f for f in self.get_frames() if f.get("cfg_id") in not_called])
        for f in not_called_frames:
            print "Not found calls for",f.tag, f.get("name"),"[cfg_id="+f.get("cfg_id")+"]", "from",f.get("label") 
        print "Processed",lcfg_xml
        print "Reachable ",len(all_called)," from ", len(all_frames)
        print len(all_frames)
        print len(all_called)
        print len(not_called)
        print all_called-all_frames
    
    def get_call_map(self):
        for call in  self.get_targeted_calls():
            if self._call_map.has_key(call.get("cfg_id")):
                self._call_map[call.get("cfg_id")].add(call)
            else:
                self._call_map[call.get("cfg_id")] = set([call])