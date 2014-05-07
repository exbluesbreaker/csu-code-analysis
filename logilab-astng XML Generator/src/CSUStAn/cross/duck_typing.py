'''
Created on 23.03.2014

@author: bluesbreaker
'''

from logilab.astng.scoped_nodes import *
from logilab.astng.node_classes import *
from pylint.pyreverse.utils import get_visibility
from CSUStAn.exceptions import CSUStAnException

class DuckTypeHandler:
    
    def __init__(self):
        pass
    
    def get_all_parents(self,class_node):
        for p in class_node.ancestors(recurs=True):
            if p.root().name.split('.')[0] == class_node.root().name.split('.')[0]:
                yield p
    
    def get_complete_signature(self,class_node):
        if hasattr(class_node, 'ucr_complete_signature'):
            return class_node.ucr_complete_signature
        ucr_complete_signature = {'attrs':class_node.ucr_complete_attrs,
                                  'methods':{m.name: m for m in class_node.methods()}}
        class_node.ucr_complete_signature = ucr_complete_signature
        return ucr_complete_signature
    
    def check_candidate(self, duck_attrs,duck_methods, cand_class, criteria='default'):
        #duck_attrs, duck_methods = self.get_duck_signature(duck)
        if (not duck_attrs) and (not duck_methods):
            return False
        candidate_signature = self.get_complete_signature(cand_class)
        candidate_attrs = candidate_signature['attrs']
        candidate_methods = set([m for m in candidate_signature['methods'].keys()])
        proper_attrs = candidate_attrs.intersection(duck_attrs)
        proper_methods = candidate_methods.intersection(duck_methods)
        value=None
        if criteria == 'default':
            if(all(attr in candidate_attrs for attr in duck_attrs) and all(method in candidate_methods for method in duck_methods)):
                return True
        elif criteria == 'capacity':
            value = float(len(proper_attrs)+len(proper_methods))/(len(duck_attrs)+len(duck_methods))
        else:
            raise CSUStAnException("Unsupported duck typing criteria!!")
        if value is not None:
            return value
        return False
    
    def get_duck_val(self,duck,names,label):
        if(duck['complex_type']):
            if duck.has_key('element_signature'):
                return sum([duck['element_signature'][label][name] for name in names])
        return sum([duck[label][name] for name in names])