'''
Created on 02.03.2014

@author: bluesbreaker
'''


from CSUStAn.astng.astng import ASTNGHandler
from CSUStAn.astng.control_flow import CFGLinker

class UCFRBuilder(ASTNGHandler):
    _project_name = None
    _out_xml = None
    def __init__(self,project,out_xml):
        self._project_name = project
        self._out_xml = out_xml
        ASTNGHandler.__init__(self,[project])
        self.run()
    def run(self):
        linker = CFGLinker(self._project_name,self._out_xml)
        linker.visit(self.project)
