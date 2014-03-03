'''
Created on 02.03.2014

@author: bluesbreaker
'''

from lxml import etree
from CSUStAn.ucfr.handling import UCFRHandler
from CSUStAn.ucr.handling import ClassIRHandler,UCRSlicer

class DataflowLinker(UCFRHandler,ClassIRHandler):
    _targeted = 0
    _out_xml = None
    _typed_ga_calls = 0
    _unknown_ga_calls = 0
    _class_dict = {}
    def __init__(self,ucr_xml,cfg_xml,out_xml):
        ClassIRHandler.__init__(self, ucr_xml)
        UCFRHandler.__init__(self, cfg_xml)
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
        print "Found ",self._targeted," UCR classes"
        print "Found getattr calls ",self._typed_ga_calls,"  unknown - ", self._unknown_ga_calls   

class InstanceInitSlicer(UCFRHandler, UCRSlicer):
    _ucr_id = None
    _keep_parents = None
    def __init__(self,ucr_xml,lcfg_xml,ucr_id,out_xml,keep_parents=False):
        UCRSlicer.__init__(self, ucr_xml)
        UCFRHandler.__init__(self, lcfg_xml)
        self._ucr_id = ucr_id
        self._keep_parents = keep_parents
        self.write_slicing(out_xml)
        
        
    def slice(self):
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
