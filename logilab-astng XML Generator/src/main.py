# -*- coding: utf-8 -*-
'''
Created on 19.08.2011

@author: bluesbreaker
'''

from os.path import join, abspath, dirname
from distutils.sysconfig import get_config_var, get_python_version

from logilab.common.modutils import file_from_modpath

STD_LIB_DIR = join(get_config_var("LIBDIR"), "python%s" % get_python_version())

from logilab.common.configuration import ConfigurationMixIn
from pylint.pyreverse.utils import insert_default_options
from logilab.astng.inspector import Linker
from lxml import etree
'''import all names of nodes'''
from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import *
from logilab.astng.manager import astng_wrapper, ASTNGManager
from logilab.astng.manager import Project
from logilab.common.modutils import get_module_part, is_relative, \
     is_standard_module
import importlib
from logilab.astng.utils import LocalsVisitor
import pydot
from reflexion.rm_tools import RMHandler


 
if __name__ == '__main__':
    pass

'''FIXME Unknown imports?'''
'''FIXME class parent is not in namespace of class?'''
'''FIXME name in except construction is not unresolved'''
'''i is not unknown in (byteplay.LOAD_FAST,i) for i in rparams'''

main_prj = None
bad_from_imports = 0
bad_imports = 0
good_imports = 0
'''Names, which not found in namespace of module, from which import is'''
unknown_name_from_module = 0

'''Number of from m import *'''
from_allimports = 0
'''Number of from m import name'''
from_imports = 0
'''From imports of module'''
from_modname_imports = 0

def write_to_namespace(node, names,type):
    if(hasattr(node, "namespace")):
        if(isinstance(names, list)):
            for name in names:
               if(not name in node.namespace[type]):
                   node.namespace[type].append(name)
        else:
            if(not names in node.namespace[type]):
                node.namespace[type].append(names)
                

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

'''Function, which compares namespace from ASTNG module node and
   from dir(module_name) after importing of this module.
   Function try to find all names from "real" module names in generated in ASTNG namespace.
   Returns number of names, which was not found'''                
def compare_namespaces(module_node):
    '''try to import modname'''
    '''FIXME Error recovery'''
    path = None
    module_node.unresolved = []
    try:
        module = importlib.import_module(module_node.name)
    except ImportError:
        return None
    names_list = dir(module)
    for name in names_list:
        if not name in module_node:
        #if(not find_in_all_namespaces(module_node, name)):
            module_node.unresolved.append(name)
            

'''Write local variable to local namespace of some frame'''
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


class UnknownSourceScope(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)


class ReflexionModelVisitor(LocalsVisitor,RMHandler):
    
    def __init__(self,project,mapping,hm_model):
        LocalsVisitor.__init__(self)
        RMHandler.__init__(self,project,mapping,hm_model)
        
    def _get_hm_module(self,source_module):
        for module in self._mapping:
            try:
                if(source_module.index(module)==0):
                    return module
            except ValueError:
                continue
        return None
    
    def extract_sm(self):
        '''Extract source model'''
        self.visit(self._project)
        
    def write_rm_to_png(self,name):
        if(self._reflexion_model is not None):
            graph = pydot.Dot(graph_type='digraph')
            node_dict = {}
            for node in self._mapping:
                dot_node = pydot.Node(node)
                graph.add_node(dot_node)
                node_dict[node] = dot_node
            for conv_source,conv_target in self._reflexion_model['convergences'].keys():
                graph.add_edge(pydot.Edge(node_dict[conv_source], node_dict[conv_target],color='green'))
            for div_source,div_target in self._reflexion_model['divergences'].keys():
                graph.add_edge(pydot.Edge(node_dict[div_source], node_dict[div_target],color='blue'))
            for absc_source,absc_target in self._reflexion_model['abscences']:
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
                '''TODO Local imports!!!!'''
                '''Only module-scoped names are interesting
                   Other names are local exactly'''
                for assign in lookup_result[1]:
                        '''Only imported names are interesting '''
                        if(isinstance(assign,From)):
                            for name in assign.names:
                                try:
                                    if(name[1]):
                                        if(expr.index(name[1])==0):
                                            call_in_module = name[0]+expr[len(name[1])+1:]+'.'+attrname
                                            if(not hasattr(assign, 'full_modname')):
                                                '''All not in-project imports will be ignored'''
                                                return
                                            target_module = assign.full_modname
                                            break
                                    else:
                                        if(expr.index(name[0])==0):
                                            call_in_module = expr+'.'+attrname
                                            if(not hasattr(assign, 'full_modname')):
                                                '''All not in-project imports will be ignored'''
                                                return
                                            target_module = assign.full_modname
                                            break
                                except ValueError:
                                    continue
                            if(call_in_module is not None):
                                break
                        elif(isinstance(assign,Import)):
                            for name in assign.names:
                                try:
                                    if(name[1]):
                                        if(expr.index(name[1])==0):
                                            '''TODO Fix this shit'''
                                            call_in_module = expr[len(name[1])+1:]
                                            if(len(call_in_module)>0):
                                                call_in_module+='.'
                                            call_in_module+=attrname
                                            if(not hasattr(assign, 'full_modname')):
                                                '''All not in-project imports will be ignored'''
                                                return
                                            target_module = assign.full_modname
                                            break
                                    else:
                                        if(expr.index(name[0])==0):
                                            '''TODO Fix this shit too'''
                                            call_in_module = expr[len(name[0])+1:]
                                            if(len(call_in_module)>0):
                                                call_in_module+='.'
                                            call_in_module+=attrname
                                            if(not hasattr(assign, 'full_modname')):
                                                '''All not in-project imports will be ignored'''
                                                return
                                            target_module = assign.full_modname
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
                            for name in assign.names:
                                try:
                                    if(name[1]):
                                        if(node.func.name == name[1]):
                                            call_in_module = name[0]
                                            if(not hasattr(assign, 'full_modname')):
                                                '''All not in-project imports will be ignored'''
                                                return
                                            target_module = assign.full_modname
                                            break
                                    else:
                                        if(node.func.name == name[0]):
                                            call_in_module = name[0]
                                            if(not hasattr(assign, 'full_modname')):
                                                '''All not in-project imports will be ignored'''
                                                return
                                            target_module = assign.full_modname
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
                    raise UnknownSourceScope(node.frame().__class__.__name__+' from '+node.root().name+' '+str(node.fromlineno))
                if(self._sm_call_deps.has_key((source_hm,target_hm))):
                    self._sm_call_deps[(source_hm,target_hm)].append((node.root().name,target_module,call_in_module,node.fromlineno,source_scope,source_object))
                else:
                    self._sm_call_deps[(source_hm,target_hm)] = [(node.root().name,target_module,call_in_module,node.fromlineno,source_scope,source_object)]             

class ReflexionModelXMLGenerator():
    def generate(self,project_name,rm_call_deps):
        root_tag = etree.Element(project_name)
        rm_tag = etree.Element("Reflexion_model")
        root_tag.append(rm_tag)
        for source,target in rm_call_deps.keys():
            dep_tag = etree.Element("Dependency")
            dep_tag.set("dep",source+","+target)
            for call in rm_call_deps[(source,target)]:
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
        return root_tag
    
class HighLevelModelDotGenerator():
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

class XMLGeneratorVisitor(LocalsVisitor):
    pass        
        
#FIXME - faster get modules
def link_imports(root_astng,linker):
    if(isinstance(root_astng, Import)):
        linker.visit_import(root_astng)
    elif(isinstance(root_astng, From)):
        linker.visit_from(root_astng)
    elif(isinstance(root_astng, Module)):
        linker.visit_module(root_astng)
    elif(isinstance(root_astng, Class)):
        linker.visit_class(root_astng)
    for child in root_astng.get_children():
        link_imports(child, linker)



''' Changed from logilab version'''
def is_standard_module(modname, std_path=(STD_LIB_DIR,)):
    """try to guess if a module is a standard python module (by default,
    see `std_path` parameter's description)

    :type modname: str
    :param modname: name of the module we are interested in

    :type std_path: list(str) or tuple(str)
    :param std_path: list of path considered has standard


    :rtype: bool
    :return:
      true if the module:
      - is located on the path listed in one of the directory in `std_path`
      - is a built-in module
    """
    global bad_imports,good_imports
    modname = modname.split('.')[0]
    try:
        filename = file_from_modpath([modname])
    except ImportError, ex:
        # import failed, i'm probably not so wrong by supposing it's
        # not standard...
        print "Unresolved Import, module name - ", modname
        bad_imports+=1
        return 0
    # modules which are not living in a file are considered standard
    # (sys and __builtin__ for instance)
    good_imports+=1
    if filename is None:
        return 1
    filename = abspath(filename)
    for path in std_path:
        path = abspath(path)
        if filename.startswith(path):
            pfx_len = len(path)
            if filename[pfx_len+1:pfx_len+14] != 'site-packages':
                return 1
            return 0
    return False



class MyLogilabLinker(Linker):
    def _imported_module(self, node, mod_path, relative):
        """notify an imported module, used to analyze dependencies
        """
        module = node.root()
        context_name = module.name
        if relative:
            mod_path = '%s.%s' % ('.'.join(context_name.split('.')[:-1]),
                                  mod_path)
        '''Save fullname for target module'''
        node.full_modname = mod_path
        if self.compute_module(context_name, mod_path):
            # handle dependencies
            if not hasattr(module, 'depends'):
                module.depends = []
            mod_paths = module.depends
            if not mod_path in mod_paths:
                mod_paths.append(mod_path)
    def visit_from(self, node):
        """visit an astng.From node
        
        resolve module dependencies
        """
        global bad_from_imports, from_modname_imports
        basename = node.modname
        context_file = node.root().file
        if context_file is not None:
            relative = is_relative(basename, context_file)
        else:
            relative = False
        for name in node.names:
            if name[0] == '*':
                fullname = basename
            else:
                fullname = '%s.%s' % (basename, name[0])
                if fullname.find('.') > -1:
                    try:
                        # XXX: don't use get_module_part, missing package precedence
                        mod_fullname = get_module_part(fullname,context_file)
                        if(mod_fullname == fullname):
                            from_modname_imports+=1;
                            node.modname_import = True;
                        fullname = mod_fullname
                    except ImportError:
                        print "Unresolved From -", node.as_string(),"File -",node.root().name,"Lineno - ",node.fromlineno 
                        bad_from_imports+=1
                        continue
            self._imported_module(node, fullname, relative)
    '''Not changed'''
    def compute_module(self, context_name, mod_path):
        """return true if the module should be added to dependencies"""
        package_dir = dirname(self.project.path)
        if context_name == mod_path:
            return 0
        elif is_standard_module(mod_path, (package_dir,)):
            return 1
        return 0

'''FIXME Bad name - no XML generated here'''
class LogilabXMLGenerator(ConfigurationMixIn):
    """"""
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        insert_default_options()
        self.manager = ASTNGManager()
        self.register_options_provider(self.manager)
        args = self.load_command_line_configuration()
        args = args[0:1]
        self.run(args)

    def run(self, args):
        """checking arguments and run project"""
        if not args:
            print self.help()
            return
        project = self.manager.project_from_files(args, astng_wrapper)
        self.project = project 
        linker = MyLogilabLinker(project, tag=True)
        link_imports(project, linker)
        '''FIXME get from file through command line'''
        mapping = ['SCons.Job',
                   'SCons.Node.FS',
                   'SCons.Action',
                   'SCons.Builder',
                   'SCons.SConf',
                   'SCons.Scanner',
                   'SCons.Script',
                   'SCons.Taskmaster',
                   'SCons.Util',
                   'SCons.Variables',
                   'SCons.Environment',
                   'SCons.Executor']
        hm_model = [('SCons.Script','SCons.Taskmaster'),
                    ('SCons.Taskmaster','SCons.SConf'),
                    ('SCons.Taskmaster','SCons.Builder'),
                    ('SCons.SConf','SCons.Environment'),
                    ('SCons.SConf','SCons.Util'),
                    ('SCons.Builder','SCons.Executor'),
                    ('SCons.Builder','SCons.Variables'),
                    ('SCons.Builder','SCons.Scanner'),
                    ('SCons.Builder','SCons.Util'),
                    ('SCons.Builder','SCons.Environment'),
                    ('SCons.Scanner','SCons.Action'),
                    ('SCons.Executor','SCons.Action'),
                    ('SCons.Action','SCons.Util'),
                    ('SCons.Action','SCons.Variables'),
                    ('SCons.Action','SCons.Job'),
                    ('SCons.Job','SCons.Util'),
                    ('SCons.Job','SCons.Node.FS')]
        rm_linker = ReflexionModelVisitor(project,mapping,hm_model)
        rm_linker.compute_rm()
        rm_linker.write_rm_to_png("SCons")
        xml_writer = ReflexionModelXMLGenerator()
        xml_root = xml_writer.generate("SCons", rm_linker._sm_call_deps)
        handle = etree.tostring(xml_root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        applic = open("SCons_rm.xml", "w")
        applic.writelines(handle)
        applic.close()
        dot_writer = HighLevelModelDotGenerator()
        graph = dot_writer.generate(mapping, hm_model)
        graph.write_png('SCons_high-level_model.png')
        
        """handler = DiadefsHandler(self.config)
        diadefs = handler.get_diadefs(project, linker)
        if self.config.output_format == "vcg":
            writer.VCGWriter(self.config).write(diadefs)
        else:
            writer.DotWriter(self.config).write(diadefs)"""    


pc = LogilabXMLGenerator(sys.argv[1:])
#main_xml_root = etree.Element("PythonSourceTree")
#ns_xml_root = etree.Element("PythonNamespaces")
#main_prj = pc.project
#make_tree(main_xml_root,pc.project)
#handle = etree.tostring(main_xml_root, pretty_print=True, encoding='utf-8', xml_declaration=True)
#main_file = "./"+sys.argv[-1]+".xml"    
#applic = open(main_file, "w")
#applic.writelines(handle)
#applic.close()
#print "bad imports - ",bad_imports,"bad from imports - ",bad_from_imports,"good - ",good_imports
#print "from imports - ",from_imports,"from * imports - ",from_allimports, "from imports of module - ", from_modname_imports
#print "not found in from imports - ", unknown_name_from_module