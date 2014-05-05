'''
Created on 02.03.2014

@author: bluesbreaker
'''


from CSUStAn.astng.astng import ASTNGHandler
from CSUStAn.astng.control_flow import UCFRLinker
from CSUStAn.cross.duck_typing import DuckTypeHandler 
from CSUStAn.exceptions import CSUStAnException
from lxml import etree

class UCFRBuilder(ASTNGHandler,DuckTypeHandler):
    _project_name = None
    _out_xml = None
    _linker = None
    def __init__(self,project,out_xml):
        self._project_name = project
        self._out_xml = out_xml
        ASTNGHandler.__init__(self,[project])
        self.run()
    def run(self):
        self._linker = UCFRLinker(self._project_name,self._out_xml)
        self._linker.visit(self.project)
        print self._linker.dbg
        self.link_duck_typing(self._linker.get_frames(),self._linker.get_classes())
        print "Processed project", self._project_name
        print "Writing",self._out_xml
        self._linker.write_result(self.project)
        
    def link_duck_typing(self,frames,classes):
        err_cnt1 = 0
        err_cnt2 = 0
        succ_cnt = 0
        err_methods = set([])
        f_num = 1
        f_len = len(frames)
        non_empty_ducks = 0
        found_ducks = 0
        for frame in frames:
            print "Processing",f_num,"frame of",f_len
            f_num+=1
            for  name in frame.duck_info.keys():
                if not frame.duck_info[name]['methods']:
                    ''' Duck without methods access doesn't need linking'''
                    continue
                all_calls = set([])
                for m in frame.duck_info[name]['methods'].keys():
                    all_calls |= frame.duck_info[name]['methods'][m]
                linked  = {m:set([]) for m in all_calls}
                if frame.duck_info[name]['attrs'] or frame.duck_info[name]['methods']:
                    non_empty_ducks += 1
                found = False
                for c in classes:
                    if self.check_candidate(frame.duck_info[name]['attrs'], frame.duck_info[name]['methods'], c):
                        target_methods = self.get_complete_signature(c)['methods']
                        for method_name in frame.duck_info[name]['methods'].keys():
                            target_method = target_methods[method_name]
                            for call in frame.duck_info[name]['methods'][method_name]:
                                call_node = self._linker.get_call(call)                               
                                if call_node is not None:
                                    if not hasattr(target_method,'id'):
                                        ''' Non-project methods or something strange '''
                                        err_cnt1 +=1
                                        err_methods.add(target_method)
                                    else:
                                        succ_cnt +=1
                                        childs = [c for c in call_node.getchildren() if c.tag=="Getattr"]
                                        if len(childs)==1:
                                            "TODO fix bug!!!!!!"
                                            if(target_method in linked[call]):
                                                continue
                                            if( not found):
                                                found = True
                                                found_ducks +=1
                                            linked[call].add(target_method)
                                            target_subnode = etree.Element("Target")
                                            target_subnode.set("type","method")
                                            target_subnode.set("cfg_id",str(target_method.id))
                                            childs[0].append(target_subnode)
                                else:
                                    ''' TODO calls in for, if etc. not handled yet'''
                                    err_cnt2 +=1
        print "Number of duck local_names",non_empty_ducks
        print "Found ducks:",found_ducks,"percentage from non-empty ducks:",found_ducks*100.0/non_empty_ducks,"%"
#         print err_cnt1, err_cnt2, succ_cnt
#                 if called=='function':
#                     target_subnode.set("type","function")
#                     if label is not None:
#                         target_subnode.set("label",label)
#                 elif called=='class':
#                     target_subnode.set("type","method")
#                     class_subnode = etree.Element("TargetClass")
#                     if label is not None:
#                         class_subnode.set("label",label)
#                     target_subnode.append(class_subnode)
#                 else:
#                     target_subnode.set("type","unknown")
#                 if called_id is not None:
#                     target_subnode.set("cfg_id",str(called_id))
#                 call_node.append(call_subnode)
