'''
Created on 02.04.2012

@author: bluesbreaker
'''

class RMHandler(object):
    '''
    Handler of reflexion models
    '''
    '''Some data for source model computation for example root node of AST'''
    _project = None
    '''Source_model_call_dependencies will be dictionary.
    Key contains (<high-level model source>,<high-level model target>) tuple for call, 
    value for this key contains list of actual calls tuples
    tuple contains concrete data about call, which may be interesting'''
    _sm_call_deps = {}
    '''Some data for compute mapping'''
    _mapping = None
    '''High-level model for reflexion model'''
    _hm_model = None
    '''Reflexion model is dictionary 
    (for details see 
    G.C. Murphy, D. Notkin, K. Sullivan / 
    Software Reflexion models: Bridging the gap between source and high-level models)
       "convergences" - dictionary of related source model calls
       "divergences" - dictionary of related source model calls
       "abscences" - list of related high-level model dependencies'''
    _reflexion_model = None
    
    def extract_sm(self):
        '''Extract source model'''
        pass
    
    def compute_rm(self):
        self.extract_sm()
        self._reflexion_model = {'convergences':{},'divergences':{},'abscences':[]}
        temp = set(list(self._sm_call_deps.keys())) | set(self._hm_model)
        for relation in (set(self._sm_call_deps.keys()) | set(self._hm_model)):
            if((relation in self._sm_call_deps.keys()) and (relation in self._hm_model)):
                self._reflexion_model['convergences'][relation] = self._sm_call_deps[relation]
            elif((relation in self._sm_call_deps.keys()) and (relation not in self._hm_model)):
                self._reflexion_model['divergences'][relation] = self._sm_call_deps[relation]
            else:
                self._reflexion_model['abscences'].append(relation)
                
    
    def __init__(self,project,mapping,hm_model):
        self._project = project
        self._mapping = mapping
        self._hm_model = hm_model
        
        