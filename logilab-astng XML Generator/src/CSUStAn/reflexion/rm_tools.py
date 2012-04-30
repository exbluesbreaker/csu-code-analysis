'''
Created on 02.04.2012

@author: bluesbreaker
'''

'''import all names of nodes'''
from logilab.astng.node_classes import CallFunc, Getattr, Const, Name, Import, From
from logilab.astng.scoped_nodes import Module, Class, Function
from logilab.astng.utils import LocalsVisitor
from CSUStAn.Exceptions import CSUStAnException
import pydot
import re
from lxml import etree

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
    sm_call_deps = None
    ''' Mapping handler'''
    _mapper = None
    '''High-level model for reflexion model'''
    _hm_model = None
    '''Reflexion model dictionary 
    (for details see 
    G.C. Murphy, D. Notkin, K. Sullivan / 
    Software Reflexion models: Bridging the gap between source and high-level models)
       "convergences" - dictionary of related source model calls
       "divergences" - dictionary of related source model calls
       "abscences" - list of related high-level model dependencies'''
    reflexion_model = None
    
    def extract_sm(self):
        '''Extract source model'''
        pass
    
    def compute_rm(self):
        self.extract_sm()
        self.reflexion_model = {'convergences':{},'divergences':{},'abscences':[]}
        temp = set(list(self.sm_call_deps.keys())) | set(self._hm_model)
        for relation in (set(self.sm_call_deps.keys()) | set(self._hm_model)):
            if((relation in self.sm_call_deps.keys()) and (relation in self._hm_model)):
                self.reflexion_model['convergences'][relation] = self.sm_call_deps[relation]
            elif((relation in self.sm_call_deps.keys()) and (relation not in self._hm_model)):
                self.reflexion_model['divergences'][relation] = self.sm_call_deps[relation]
            else:
                self.reflexion_model['abscences'].append(relation)
                
    
    def __init__(self,project,mapper,hm_model):
        self._project = project
        self._mapper = mapper
        self._hm_model = hm_model
        self.sm_call_deps = {}
        
class ReflexionModelVisitor(LocalsVisitor,RMHandler):
    """Visit ASTNG project and compute reflexion model for it"""
    
    """List of modules, which have ignored, according to given mapping"""
    ignored_modules = []
    
    def __init__(self,project,mapper,hm_model):
        LocalsVisitor.__init__(self)
        RMHandler.__init__(self,project,mapper,hm_model)
        
    def _get_hm_module(self,source_module):
        return self._mapper.map(source_module)
    
    def extract_sm(self):
        '''Extract source model'''
        self.visit(self._project)
        
    def write_rm_to_png(self,name):
        if(self.reflexion_model is not None):
            graph = pydot.Dot(graph_type='digraph')
            node_dict = {}
            for node in self._mapper.get_hm_entities():
                dot_node = pydot.Node(node)
                graph.add_node(dot_node)
                node_dict[node] = dot_node
            for conv_source,conv_target in self.reflexion_model['convergences'].keys():
                graph.add_edge(pydot.Edge(node_dict[conv_source], node_dict[conv_target],color='green',label=str(len(self.reflexion_model['convergences'][conv_source,conv_target]))))
            for div_source,div_target in self.reflexion_model['divergences'].keys():
                graph.add_edge(pydot.Edge(node_dict[div_source], node_dict[div_target],color='blue',label=str(len(self.reflexion_model['divergences'][div_source,div_target]))))
            for absc_source,absc_target in self.reflexion_model['abscences']:
                graph.add_edge(pydot.Edge(node_dict[absc_source], node_dict[absc_target],color='red'))
            graph.write_png(name+'_reflexion_model.png')
        
    
    def visit(self, node):
        """launch the visit starting from the given node"""
        if self._visited.has_key(node):
            return
        self._visited[node] = 1 
        methods = self.get_callbacks(node)
        if methods[0] is not None:
            methods[0](node)
        for child in node.get_children():
            self.visit(child)
            
    def visit_module(self,node):
        """Check, if module will be ignored"""
        if self._get_hm_module(node.name) is None:
            self.ignored_modules.append(node.name)
    

    
    def visit_callfunc(self, node):
        call_in_module = None # that was called in target module
        target_module = None
        if(isinstance(node.func,Getattr)):
            call = list(node.get_children())[0]
            attrname = call.attrname
            expr = call.expr.as_string()
            while(not isinstance(call, Name) and not isinstance(call,Const)):
                call = list(call.get_children())[0]
            '''Something like "abcd".join() will be ignored'''
            if(isinstance(call, Const)):
                return
            '''Now call must be Name node'''
            lookup_result = call.lookup(call.name)
            if(isinstance(lookup_result[0],Module)):
                '''TODO Local imports(imports in function or class)'''
                '''Only module-scoped names are interesting
                   Other names are local exactly'''
                for assign in lookup_result[1]:
                        '''Only imported names are interesting '''
                        if(isinstance(assign,From)):
                            if(not hasattr(assign, 'full_modnames')):
                                '''All not in-project imports will be ignored'''
                                return
                            full_modname_iter = iter(assign.full_modnames)
                            for name in assign.names:
                                try:
                                    if(name[1]):
                                        if(expr.index(name[1])==0):
                                            call_in_module = name[0]+expr[len(name[1])+1:]+'.'+attrname
                                            target_module = full_modname_iter.next()
                                            break
                                    else:
                                        if(expr.index(name[0])==0):
                                            call_in_module = expr+'.'+attrname
                                            target_module = full_modname_iter.next()
                                            break
                                except ValueError:
                                    continue
                            if(call_in_module is not None):
                                break
                        elif(isinstance(assign,Import)):
                            if(not hasattr(assign, 'full_modnames')):
                                '''All not in-project imports will be ignored'''
                                return
                            full_modname_iter = iter(assign.full_modnames)
                            for name in assign.names:
                                try:
                                    if(name[1]):
                                        if(expr.index(name[1])==0):
                                            '''TODO Fix this shit'''
                                            call_in_module = expr[len(name[1])+1:]
                                            if(len(call_in_module)>0):
                                                call_in_module+='.'
                                            call_in_module+=attrname
                                            target_module = full_modname_iter.next()
                                            break
                                    else:
                                        if(expr.index(name[0])==0):
                                            '''TODO Fix this shit too'''
                                            call_in_module = expr[len(name[0])+1:]
                                            if(len(call_in_module)>0):
                                                call_in_module+='.'
                                            call_in_module+=attrname
                                            target_module = full_modname_iter.next()
                                            break
                                except ValueError:
                                    continue
                            if(call_in_module is not None):
                                break
        elif(isinstance(node.func,Name)):
            lookup_result = node.func.lookup(node.func.name)
            if(isinstance(lookup_result[0],Module)):
                '''TODO Local imports!!!!'''
                '''Only module-scoped names are interesting
                   Other names are local exactly'''
                call_in_module = None # that was called in target module
                target_module = None
                for assign in lookup_result[1]:
                        '''Only imported names are interesting '''
                        if(isinstance(assign,From)):
                            if(not hasattr(assign, 'full_modnames')):
                                '''All not in-project imports will be ignored'''
                                return
                            full_modname_iter = iter(assign.full_modnames)
                            for name in assign.names:
                                try:
                                    if(name[1]):
                                        if(node.func.name == name[1]):
                                            call_in_module = name[0]
                                            target_module = full_modname_iter.next()
                                            break
                                    else:
                                        if(node.func.name == name[0]):
                                            call_in_module = name[0]
                                            target_module = full_modname_iter.next()
                                            break
                                except ValueError:
                                    continue
                            if(call_in_module is not None):
                                break
        
        if((target_module is not None)and(call_in_module is not None)):
            source_hm = self._get_hm_module(node.root().name)
            target_hm = self._get_hm_module(target_module)
            if((source_hm is not None)and(target_hm is not None)and(source_hm!=target_hm)):
                source_scope = None
                source_object = None
                if(isinstance(node.frame(),Function)):
                    if(isinstance(node.frame().parent,Class)):
                        '''Call from class method'''
                        source_scope = 'class_method'
                        source_object = node.frame().parent.name+'.'+node.frame().name
                    else:
                        '''Call from function'''
                        source_scope = 'function'
                        source_object = node.frame().name
                elif(isinstance(node.frame(),Module)):
                    '''Call from module'''
                    source_scope = 'module'
                elif(isinstance(node.frame(),Class)):
                    source_scope = 'class'
                    source_object = node.frame().name
                else:
                    '''Something else and strange'''
                    raise CSUStAnException(node.frame().__class__.__name__+' from '+node.root().name+' '+str(node.fromlineno))
                if(self.sm_call_deps.has_key((source_hm,target_hm))):
                    self.sm_call_deps[(source_hm,target_hm)].append((node.root().name,target_module,call_in_module,node.fromlineno,source_scope,source_object))
                else:
                    self.sm_call_deps[(source_hm,target_hm)] = [(node.root().name,target_module,call_in_module,node.fromlineno,source_scope,source_object)]

class RMMapper():
    """Return high-level entity for given source entity"""
    _mapping = None
    def map(self,sorce_entity):
        pass
    """Return high-level entities"""
    def get_hm_entities(self):
        pass
    
class RegexMapper(RMMapper):
    """Use regular expressions based mapping"""
    """Regex must be passed as unicode string, simple string - for direct mapping"""
    """Mapping example:
            {'A': ['Package1.module1', 'Package1.module2']
             'B':[u'Package1\.pack2.*']} """
    def __init__(self,**kwargs):
        for key in kwargs:
            if(key=='mapping'):
                if(not isinstance(kwargs[key],dict)):
                    raise TypeError('Mapping must be dictionary!')
                self._mapping = kwargs[key]
    def map(self,source_entity):
        for rule in self._mapping:
            for regex in self._mapping[rule]:
                if(isinstance(regex, unicode)):
                    if(re.match(regex, source_entity) is not None):
                        return rule
                else:
                    if(regex == source_entity):
                        return rule
        return None
    def get_hm_entities(self):
        return self._mapping.keys()
                                 
class SourceModelXMLGenerator():
    """Generate Calls XML  for given source model"""
    root_tag = None
    def generate(self,project_name,sm_call_deps,ignored_modules):
        root_tag = etree.Element(project_name)
        ignored_tag = etree.Element("Ignored")
        root_tag.append(ignored_tag)
        for module in ignored_modules:
            ignored_module_tag = etree.Element("Module")
            ignored_module_tag.set("name",module)
            ignored_tag.append(ignored_module_tag)
        rm_tag = etree.Element("Reflexion_model")
        root_tag.append(rm_tag)
        for source,target in sm_call_deps.keys():
            dep_tag = etree.Element("Dependency")
            dep_tag.set("dep",source+","+target)
            for call in sm_call_deps[(source,target)]:
                call_tag = etree.Element("Call")
                call_tag.set("source_module",call[0])
                call_tag.set("target_module",call[1])
                call_tag.set("called_object",call[2])
                call_tag.set("source_fromlineno",str(call[3]))
                call_tag.set("source_scope",call[4])
                if(call[5] is not None):
                    call_tag.set("source_object",call[5])
                dep_tag.append(call_tag)
            rm_tag.append(dep_tag)
        self.root_tag = root_tag
    def write_to_file(self,filename):
        if(self.root_tag is not None):
                    handle = etree.tostring(self.root_tag, pretty_print=True, encoding='utf-8', xml_declaration=True)
                    applic = open(filename, "w")
                    applic.writelines(handle)
                    applic.close()
    
class HighLevelModelDotGenerator():
    """Generate image for given high-level model"""
    def generate(self,nodes,deps):
        graph = pydot.Dot(graph_type='digraph')
        node_dict = {}
        for node in nodes:
            dot_node = pydot.Node(node)
            graph.add_node(dot_node)
            node_dict[node] = dot_node
        for source, target in deps:
            graph.add_edge(pydot.Edge(node_dict[source], node_dict[target]))
        return graph
        
        