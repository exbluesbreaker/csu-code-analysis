'''
Created on 14.04.2013

@author: bluesbreaker
'''
from pylint.pyreverse.utils import insert_default_options
from pylint.pyreverse.main import OPTIONS
from logilab.astng.manager import astng_wrapper, ASTNGManager
from logilab.common.configuration import ConfigurationMixIn

class ASTNGHandler(ConfigurationMixIn):
    
    options = OPTIONS
    
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        insert_default_options()
        self.manager = ASTNGManager()
        self.register_options_provider(self.manager)
        args = self.load_command_line_configuration()
        project = self.manager.project_from_files(args, astng_wrapper)
        self.project = project