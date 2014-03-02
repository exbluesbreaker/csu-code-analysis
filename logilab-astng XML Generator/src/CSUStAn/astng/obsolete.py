'''
Created on 07.04.2012

@author: bluesbreaker
'''
from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import *
from logilab.common.configuration import ConfigurationMixIn
from logilab.astng.manager import astng_wrapper, ASTNGManager

from pylint.pyreverse.diadefslib import DiadefsHandler
from pylint.pyreverse.utils import insert_default_options
from pylint.pyreverse.main import OPTIONS

from lxml import etree
import re

from CSUStAn.astng.inspector import NoInferLinker


'''Old "hand-made" namespaces generation tools '''
''' must be set before call of functions'''
main_prj = None
'''FIXME Unknown imports?'''
'''FIXME class parent is not in namespace of class?'''
'''FIXME name in except construction is not unresolved'''
'''i is not unknown in (byteplay.LOAD_FAST,i) for i in rparams'''
def find_in_namespace(namespace,name):
    for key in namespace.keys():
        for target_name in namespace[key]:
            if(name==target_name[0]):
                name_type = target_name[1]
                name_source = key
                return name_type,name_source, key
    return None

'''FIXME Support for builtin namespace'''
'''FIXME Correct support of name defined as global'''
def find_in_all_namespaces(node,name,scope='local'):
    current_frame = node.frame()
    if(isinstance(current_frame, Class)):
        ''' Fields and methods not visible for class's methods
            and class's namespace will be ignored'''
        return find_in_all_namespaces(current_frame.parent.frame(), name, 'nonlocal')
    def_type = find_in_namespace(current_frame.namespace,name)
    if(def_type):
        if(isinstance(current_frame, Module)):
            return 'global', def_type[0], def_type[1]
        else:
            return scope, def_type[0], def_type[1]
    else:
        if(isinstance(current_frame, Module)):
            ''' Find builtin name '''
            for builtin_name in (dir(__builtins__)):
                if(builtin_name == name):
                    return 'builtin','builtin_name','__builtins__'
            return None
        return find_in_all_namespaces(current_frame.parent.frame(), name, 'nonlocal')
    
'''Write local variable to local namespace of some frame'''
def write_to_namespace(node, names,type):
    if(hasattr(node, "namespace")):
        if(isinstance(names, list)):
            for name in names:
               if(not name in node.namespace[type]):
                   node.namespace[type].append(name)
        else:
            if(not names in node.namespace[type]):
                node.namespace[type].append(names)
                
def add_local_name(node,name):
    if(isinstance(node.statement(), Function)):
        '''Function argument'''
        write_to_namespace(node.frame(),(name,'argument'),'this_module') 
    elif(isinstance(node.statement(), (Assign,For,AugAssign,Discard))):
        if(isinstance(node.frame(), Class)):
            '''Field of class'''
            write_to_namespace( node.frame(),(name,'field'),'this_module')
        else:
            '''Variable in module or func'''
            write_to_namespace( node.frame(),(name,'var'),'this_module')
    elif(isinstance(node.statement(), ExceptHandler)):
        write_to_namespace(node.frame(),(name,'except_argument'),'this_module') 
    else:
        print node.statement().__class__.__name__, node.name, node.statement().as_string()

''' Init namespaces, make local namespaces for modules and make local resolving '''
def make_local_namespaces(root_astng):
    if(isinstance(root_astng, Module)):
        if(hasattr(root_astng, 'namespace')):
            print "Error Node Module allready have namespace"
        else:
            '''Init namespace for module'''
            root_astng.namespace = {'this_module':[],'unknown': [],'imports':[]}
            root_astng.unresolved = []
    elif(isinstance(root_astng, AssName)):
        ''' Find type of name (field,argument, var etc.) 
            and add it to namespace, if it needed '''
        add_local_name(root_astng,root_astng.name)
    elif(isinstance(root_astng, Class)):
        ''' Frame for class is class itself, and Class 
            name must be added to higher level namespace'''
        write_to_namespace(root_astng.parent.frame(), (root_astng.name,'class'),'this_module')
        if(hasattr(root_astng, 'namespace')):
            print "Error Node Class allready have namespace"
        else:
            '''Init namespace for class'''
            root_astng.namespace = {'this_module':[],'unknown': [],'imports':[],'global':[]}
            root_astng.unresolved = []
    elif(isinstance(root_astng, Function)):
        ''' Frame for func is func itself'''
        write_to_namespace(root_astng.parent.frame(), (root_astng.name,'func'),'this_module')
        if(hasattr(root_astng, 'namespace')):
            print root_astng.namespace
            print "Error Node Function allready have namespace"
        else:
            '''Init namespace for function'''
            root_astng.namespace = {'this_module':[],'unknown': [],'imports':[],'global':[]}
            root_astng.unresolved = []
    elif(isinstance(root_astng, Lambda)):
        #write_to_namespace(root_astng.frame(), (root_astng.name,'lambda'),'this_module')
        if(hasattr(root_astng, 'namespace')):
            print "Error Node Lambda allready have namespace"
        else:
            '''Init namespace for lambda'''
            root_astng.namespace = {'this_module':[],'unknown': [],'imports':[],'global':[]}
            root_astng.unresolved = []
    elif(isinstance(root_astng, Name)):
        ''' For NodeNG frame returns first parent frame node(module, class, func)!'''
        '''FIXME func arguments is not unresolved!!!'''
        if(hasattr(root_astng.frame(), "namespace")):
            def_type = find_in_namespace(root_astng.frame().namespace, root_astng.name)
            if(def_type):
                root_astng.name_scope = 'local'
                root_astng.name_type = def_type[0]
                root_astng.name_source = def_type[1]
    elif(isinstance(root_astng, Global)):
        for name in root_astng.names:
            '''Find name in global namespace'''
            '''def_typr is tuple 1 is type, 2 is source'''
            def_type = find_in_namespace(root_astng.root().namespace, name)
            if(not def_type):
                write_to_namespace(root_astng.root(), (name,def_type[0]), 'this_file')
            write_to_namespace(root_astng.frame(), (name,def_type[0]), 'global')
    for child in root_astng.get_children():
        make_local_namespaces(child)
        
''' Make namespaces for modules and make resolving '''
def make_namespaces(root_astng):
    #if(hasattr(root_astng, "full_modname")):
     #   if(main_prj.locals.has_key(root_astng.full_modname)):
      #      print root_astng.full_modname
    global from_allimports,from_imports, unknown_name_from_module
    if(isinstance(root_astng, Import)):
        for name in root_astng.names:
            if (name[1]):
                '''FIXME detect type of imported name - class or func'''
                write_to_namespace(root_astng.frame(), (name[1],'mod_name'),'imports')
            else:
                write_to_namespace(root_astng.frame(), (name[0],'mod_name'),'imports')
    elif(isinstance(root_astng, From)):
        #print root_astng.as_string()
        for name in root_astng.names:
            if(hasattr(root_astng, "full_modname")):
                try:
                    target_module = main_prj.get_module(root_astng.full_modname)
                    if(name[0] == '*'):
                        from_allimports+=1
                        write_to_namespace(root_astng.frame(), target_module.namespace['this_module'],'imports')
                        write_to_namespace(root_astng.frame(), target_module.namespace['unknown'],'imports')
                    else:
                        from_imports+=1
                        '''Import of modname (not name from module)'''
                        if(hasattr(root_astng,'modname_import')):
                            if(name[1]):
                                write_to_namespace(root_astng.frame(), (name[1],'mod_name'),'imports')
                            else:
                                write_to_namespace(root_astng.frame(), (name[0],'mod_name'),'imports')
                        else:
                            found = False
                            for key in target_module.namespace.keys():
                                for target_name in target_module.namespace[key]:
                                    if(name[0]==target_name[0]):
                                        ''' name[1] is asname '''
                                        if(name[1]):
                                            write_to_namespace(root_astng.frame(), (name[1],target_name[1]),'imports')
                                            found = True
                                            break
                                        else:
                                            write_to_namespace(root_astng.frame(), (name[0],target_name[1]),'imports')
                                            found = True
                                            break
                                if(found):
                                    break
                            '''Names, which was imported with From construction, but can't be resolved 
                               (this name not found in target namespace)'''
                            if(not found):
                                if(name[1]):
                                    write_to_namespace(root_astng.frame(), (name[1],'unknown_name'),'imports')
                                else:
                                    write_to_namespace(root_astng.frame(), (name[0],'unknown_name'),'imports')
                                unknown_name_from_module +=  1
                                
                except KeyError:
                    pass
                    #root_astng.root.unresolved +=1
            else:
                ''' Source module for import not found,
                    but imported name will be added to namespace, if it not * import'''
                if(name[0] != '*'):
                     if(name[1]):
                         write_to_namespace(root_astng.frame(), (name[1],'unknown_name'),'imports')
                     else:
                         write_to_namespace(root_astng.frame(), (name[0],'unknown_name'),'imports')
    elif(isinstance(root_astng, Name)):
        '''If name allready resolved'''
        if(not hasattr(root_astng, "name_type")):
            if(hasattr(root_astng.frame(), "namespace")):
                def_name = find_in_all_namespaces(root_astng,root_astng.name)
                if(def_name):
                    root_astng.name_scope = def_name[0]
                    root_astng.name_type = def_name[1]
                    root_astng.name_source = def_name[2]
                else:
                    if(not root_astng.name in root_astng.frame().unresolved):
                        root_astng.frame().unresolved.append(root_astng.name) # name is not in namespace
    for child in root_astng.get_children():
        make_namespaces(child)
        
class LogilabUCRBuilder(ConfigurationMixIn):
    ''' generate XML, describing classes of project '''
    
    options = OPTIONS
    
    _good_gettatr = 0
    _bad_gettatr = 0
    # numbers of "ducks" in project (for complexity estimation)
    _all_ducks = 0
    # numbers of classes in project (for complexity estimation)
    _all_classes = 0
    _process_candidates = False
    _ducks_count = 0
    _found_ducks = 0
    _prob_used_classes = None
    _all_attrs_num = 0
    _complex_ducks = 0
    _assigned_ducks = 0
    _dbg_assattr_parents = None 
    _list_attrs = [attr for attr in dir([]) if not re.search('\A(?!_)',attr)]
    _list_methods = [attr for attr in dir([]) if re.search('\A(?!_)',attr)]
    _dict_attrs = [attr for attr in dir({}) if not re.search('\A(?!_)',attr)]
    _dict_methods = [attr for attr in dir({}) if re.search('\A(?!_)',attr)]
    _tuple_attrs = [attr for attr in dir(()) if not re.search('\A(?!_)',attr)]
    _tuple_methods = [attr for attr in dir(()) if re.search('\A(?!_)',attr)]
    _attr_iteration_cycles = 0
    _processed_methods = 0
    
    def __init__(self, args,process_candidates=False):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        self._prob_used_classes = Set([])
        self._dbg_assattr_parents = Set([])
        self._process_candidates = process_candidates
        insert_default_options()
        self.manager = ASTNGManager()
        self.register_options_provider(self.manager)
        args = self.load_command_line_configuration()
        self.run(args)
      
    """ Extract information about class signature - attrs and methods, which it have """    
    def _compute_signature(self,node):
        if(hasattr(node, "csu_complete_signatures")):
            # node have been processed already
            return node.csu_complete_signatures
        else:
            node.csu_complete_signatures={}
        node.csu_complete_signatures['Attrs'] = Set([re.search('[^ :]*',attr).group(0) for attr in node.attrs])
        node.csu_complete_signatures['Methods'] = Set([meth.name for meth in node.methods])
        # class without parents
        if not hasattr(node, "csu_parents"):
            node.csu_parents = []
        parents = node.csu_parents
        for parent in parents:
            parent_signature = self._compute_signature(parent)
            # append all parents signatures
            node.csu_complete_signatures['Attrs'] |= parent_signature['Attrs']
            node.csu_complete_signatures['Methods'] |= parent_signature['Methods']
        return node.csu_complete_signatures
    
    """ Check body of cycle, which iterating over class's field"""
    def _check_cycle(self,node,iter_name,attr,duck_dict):
        if isinstance(node, Getattr):
            if(node.expr.as_string()==iter_name):
                if(not duck_dict[attr].has_key('element_signature')):
                           duck_dict[attr]['element_signature']={'attrs':Set([]),'methods':Set([])} 
                if isinstance(node.parent,CallFunc):
                    duck_dict[attr]['element_signature']['methods'].add(node.attrname)
                else:
                    duck_dict[attr]['element_signature']['attrs'].add(node.attrname)           
        for child in node.get_children():
            duck_dict = self._check_cycle(child,iter_name,attr,duck_dict)
        return duck_dict
    
    """ Extract information about class fields usage """
    def _extract_duck_info(self,node,attrs,duck_dict=None):
        if(duck_dict is None):
            duck_dict = {}
        if isinstance(node, Getattr):
            if(node.expr.as_string()=="self"):
                if isinstance(node.parent, For):
                    if(not duck_dict.has_key(node.attrname)):
                        self._ducks_count +=1
                        duck_dict[node.attrname] = {'attrs':Set([]),'methods':Set([]),'type':[],'complex_type':'Unknown','assigned':False}
                    self._attr_iteration_cycles +=1
                    if isinstance(node.parent.target, AssName):
                        print node.parent.as_string()
                        for body in node.parent.body:
                            duck_dict = self._check_cycle(body,node.parent.target.name,node.attrname,duck_dict)
                if(node.attrname not in attrs):
                    #print node.attrname,node.parent, node.fromlineno, node.root()
                    #print attrs
                    self._bad_gettatr+=1
                else:
                    self._good_gettatr+=1
                # if additional info about attr's field may be obtained
                if isinstance(node.parent, Getattr):
                    #init dict for attr
                    if(not duck_dict.has_key(node.attrname)):
                        self._ducks_count +=1
                        duck_dict[node.attrname] = {'attrs':Set([]),'methods':Set([]),'type':[],'complex_type':None,'assigned':False}
                    if isinstance(node.parent.parent,CallFunc):
                        #we get info about attr's method
                        duck_dict[node.attrname]['methods'].add(node.parent.attrname)
                    else:
                        #we get info about attr's attr
                        duck_dict[node.attrname]['attrs'].add(node.parent.attrname)
                # attr of complex type (list, dict, tuple etc.)
                elif isinstance(node.parent, Subscript):
                    if(not duck_dict.has_key(node.attrname)):
                        self._ducks_count +=1
                        duck_dict[node.attrname] = {'attrs':Set([]),'methods':Set([]),'type':[],'complex_type':'Unknown','assigned':False}
                    else:
                        duck_dict[node.attrname]['complex_type'] = 'Unknown'
                    if(isinstance(node.parent.parent,Getattr)):
                       # get some info about element of complex type
                       if(not duck_dict[node.attrname].has_key('element_signature')):
                           duck_dict[node.attrname]['element_signature']={'attrs':Set([]),'methods':Set([])}
                       if isinstance(node.parent.parent.parent,CallFunc):
                           duck_dict[node.attrname]['element_signature']['methods'].add(node.parent.parent.attrname)
                       else:
                           duck_dict[node.attrname]['element_signature']['attrs'].add(node.parent.parent.attrname)
        elif isinstance(node, AssAttr):
            if(node.expr.as_string()=="self"):
                if(not duck_dict.has_key(node.attrname)):
                    self._ducks_count +=1
                    self._assigned_ducks +=1
                    duck_dict[node.attrname] = {'attrs':Set([]),'methods':Set([]),'type':[],'complex_type':None,'assigned':True} 
                else:
                    if(not duck_dict[node.attrname]['assigned']):
                        duck_dict[node.attrname]['assigned'] = True
                        self._assigned_ducks+=1
                # DEBUG
                if (not node.parent.__class__.__name__ in self._dbg_assattr_parents):
                    self._dbg_assattr_parents |= Set([node.parent.__class__.__name__])
                    print node.parent.__class__.__name__
                    if(isinstance(node.parent, Tuple)):
                        print node.parent.as_string()
                # DEBUG END
                if(isinstance(node.parent, (Assign,AugAssign))):
                    if(isinstance(node.parent.value, (Tuple,Dict,List))):
                        duck_dict[node.attrname]['complex_type'] = node.parent.value.__class__.__name__ 
        for child in node.get_children():
            duck_dict = self._extract_duck_info(child,attrs,duck_dict)
        return duck_dict
    
    # Check if object is of standard complex type(dict, tuple or list)
    def _check_complex_type(self,attrs,methods):
        if(all(meth in self._list_methods for meth in methods) and
           all(attr in self._list_attrs for attr in attrs)):
            return 'List'
        elif(all(meth in self._dict_methods for meth in methods) and
             all(attr in self._dict_attrs for attr in attrs)):
            return 'Dict'
        elif(all(meth in self._tuple_methods for meth in methods) and
             all(attr in self._tuple_attrs for attr in attrs)):
            return 'Tuple'
        return None

    def run(self, args):
        """checking arguments and run project"""
        if not args:
            print self.help()
            return
        project = self.manager.project_from_files(args, astng_wrapper)
        self.project = project
        linker = NoInferLinker(project, tag=True)
        handler = DiadefsHandler(self.config)
        diadefs = handler.get_diadefs(project, linker)
        # Add inheritance information to nodes
        # csu_parents will contain links to all parents of class
        for rel in diadefs[-1].relationships['specialization']:
            if hasattr(rel.from_object, "csu_parents"):
                rel.from_object.csu_parents.append(rel.to_object)
            else:
                rel.from_object.csu_parents=[rel.to_object]
        bad_ducks = 0
        empty_ducks = 0
        # First pass for collecting "duck" information about fields 
        for obj in diadefs[-1].objects:
            self._compute_signature(obj)
            attr_names = [re.search('[^ :]*',s).group(0) for s in obj.attrs]
            self._all_attrs_num += len(Set(attr_names))
            attr_names+= [m.name for m in obj.methods]
            duck_dict = None
            for meth in obj.methods:
                # check self access in method and generate information about class attrs 
                if(self._process_candidates):
                    duck_dict =  self._extract_duck_info(meth,attr_names,duck_dict)
                self._processed_methods += 1
            # add duck information to classes
            obj.ducks=duck_dict
        successes = 0
        #Second pass  for processing "duck" information and generate information about types
        for current_class in diadefs[-1].objects:
            if (current_class.ducks is None):
                continue
            for duck in current_class.ducks.keys():
                if(current_class.ducks[duck]['complex_type']):
                    self._complex_ducks +=1
                    #self._found_ducks+=1
                    # duck is complex type, nothing to do with it
                    # TODO recursively complex types
                    if current_class.ducks[duck].has_key('element_signature'):
                        # search for class of element is needed 
                        duck_attrs = current_class.ducks[duck]['element_signature']['attrs']
                        duck_methods = current_class.ducks[duck]['element_signature']['methods']
                    else:
                        # duck of complex type and no duck info about element
                        empty_ducks += 1
                        continue
                else:
                    duck_attrs = current_class.ducks[duck]['attrs']
                    duck_methods = current_class.ducks[duck]['methods']
                # ignore empty ducks
                if((not duck_attrs) and (not duck_methods)):
                    empty_ducks += 1
                    continue
                duck_found = False
                for field_candidate in diadefs[-1].objects:
                    complex_type = self._check_complex_type(duck_attrs, duck_methods)
                    if(complex_type):
                        #DEBUG
                        if(current_class.ducks[duck]['complex_type']):
                            if((current_class.ducks[duck]['complex_type'] != complex_type) 
                               and (current_class.ducks[duck]['complex_type'] !='Unknown')):
                                print current_class.ducks[duck]['complex_type'], complex_type
                        #END DEBUG
                        current_class.ducks[duck]['complex_type'] = complex_type
                        if(not duck_found):
                            self._found_ducks+=1
                            duck_found = True
                    if(all(attr in field_candidate.csu_complete_signatures['Attrs'] for attr in duck_attrs) and all(method in field_candidate.csu_complete_signatures['Methods'] for method in duck_methods)):
                        current_class.ducks[duck]['type'].append(field_candidate)
                        successes += 1
                        self._prob_used_classes |= Set([field_candidate.fig_id])
                        if(not duck_found):
                            self._found_ducks+=1
                            duck_found = True
                #check if duck not found at all
                if(not duck_found):
                    bad_ducks += 1
                    print "Bad duck - ",duck_attrs, duck_methods     
        print "Bad ducks ", bad_ducks
        print "Empty ducks ", empty_ducks                    
        print "Numbers of ducks: ", self._ducks_count
        print "Numbers of ducks with assignment in class: ", self._assigned_ducks
        print "Numbers of ducks with complex type: ", self._complex_ducks
        print "Found ducks: ",self._found_ducks, " percentage: ",round(100*float(self._found_ducks)/self._ducks_count,1), " %"
        print "Numbers of all attributes in project: ", self._all_attrs_num, " percentage of found attrs: ",round(100*float(self._found_ducks)/self._all_attrs_num,1), " %"
        print "Numbers of classes: ",len(diadefs[-1].objects)
        print "Probably used (as field) classes: ",len(self._prob_used_classes)," percentage: ",round(100*float(len(self._prob_used_classes))/len(diadefs[-1].objects),1), " %"
        print "Processed methods: ", self._processed_methods
        
        """ result XML generation """
        mapper = {}
        root = etree.Element("Classes")
        for obj in diadefs[-1].objects:
            self._all_classes +=1
            node = etree.Element("Class",name=obj.title,id=str(obj.fig_id),label=obj.node.root().name)
            mapper[obj] = node
            root.append(node)
            for attrname in Set([re.search('[^ :]*',attr).group(0) for attr in obj.attrs]):
                attr_node = etree.Element('Attr',name=attrname,modifier='public')
                node.append(attr_node)
                if(obj.ducks and (attrname in obj.ducks)):
                    if obj.ducks[attrname]['complex_type']:
                        for prob_type in obj.ducks[attrname]['type']:
                            attr_node.append(etree.Element('AggregatedType',type=str(obj.ducks[attrname]['complex_type']),element=prob_type.title,id=str(prob_type.fig_id)))
                    else:
                        for prob_type in obj.ducks[attrname]['type']:
                            attr_node.append(etree.Element('CommonType',name=prob_type.title,id=str(prob_type.fig_id)))       
            for meth in obj.methods:
                meth_node = etree.Element('Method',name=meth.name,modifier='public')
                # This is needed for some native libs(pyx)
                if(meth.args.args == None):
                    continue
                for arg in meth.args.args:
                    # ignore self arg
                    if not arg.name == 'self':
                        meth_node.append(etree.Element('Arg',name=arg.name))
                node.append(meth_node)
        for rel in diadefs[-1].relationships['specialization']:
            mapper[rel.from_object].append(etree.Element('Parent',name=rel.to_object.title,id=str(rel.to_object.fig_id)))
        f = open('test.xml','w')
        f.write(etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
        print len(diadefs[-1].relationships['specialization'])
        #print self._good_gettatr,self._bad_gettatr
        #print self._all_ducks
        
        #print self._all_classes