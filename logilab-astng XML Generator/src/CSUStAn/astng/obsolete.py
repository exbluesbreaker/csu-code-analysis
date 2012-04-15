'''
Created on 07.04.2012

@author: bluesbreaker
'''
from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import *
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