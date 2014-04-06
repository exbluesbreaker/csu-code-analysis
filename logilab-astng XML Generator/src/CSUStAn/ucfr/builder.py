'''
Created on 02.03.2014

@author: bluesbreaker
'''


from CSUStAn.astng.astng import ASTNGHandler
from CSUStAn.astng.control_flow import UCFRLinker
from CSUStAn.cross.duck_typing import DuckTypeHandler 
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
        self._linker.write_result(self.project)
        
    def link_duck_typing(self,frames,classes):
        err_cnt1 = 0
        err_cnt2 = 0
        succ_cnt = 0
        err_methods = set([])
        for frame in frames:
            for  name in frame.duck_info.keys():
                if not frame.duck_info[name]['methods']:
                    ''' Duck without methods access doesn't need linking'''
                    continue
                for c in classes:
                    if self.check_candidate(frame.duck_info[name]['attrs'], frame.duck_info[name]['methods'], c):
                        target_methods = self.get_complete_signature(c)['methods']
                        for method_name in frame.duck_info[name]['methods'].keys():
                            target_method = target_methods[method_name]
                            for call in frame.duck_info[name]['methods'][method_name]:
                                call_node = self._linker.get_call(call)
                                if call_node:
                                    if not hasattr(target_method,'id'):
                                        ''' Non-project methods or something strange '''
                                        err_cnt1 +=1
                                        err_methods.add(target_method)
                                    else:
                                        succ_cnt +=1
                                        target_subnode = etree.Element("Target")
                                        target_subnode.set("type","method")
                                        target_subnode.set("cfg_id",str(target_method.id))
                                        call_node.append(target_subnode)
                                else:
                                    ''' TODO calls in for, if etc. not handled yet'''
                                    err_cnt2 +=1
        print err_cnt1, err_cnt2, succ_cnt
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
