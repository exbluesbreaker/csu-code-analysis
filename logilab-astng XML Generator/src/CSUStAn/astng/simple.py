'''
Created on 02.04.2012

@author: bluesbreaker
'''

from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import *
from logilab.astng.manager import Project
from logilab.common.modutils import file_from_modpath, get_module_part, is_relative, is_standard_module
from logilab.astng.inspector import Linker
from distutils.sysconfig import get_config_var, get_python_version
from os.path import join, abspath, dirname
from lxml import etree



STD_LIB_DIR = join(get_config_var("LIBDIR"), "python%s" % get_python_version())


'''Collect some info about importss'''
class NamesCheckLinker(Linker):
    '''From and Import will have full_modname field, if it is in-project import'''
    bad_from_imports = 0
    bad_imports = 0
    good_imports = 0
    '''Number of from m import *'''
    from_allimports = 0
    '''Number of from m import name'''
    from_imports = 0
    '''From imports of module'''
    from_modname_imports = 0
    ''' Changed version of similiar function logilab.common.modutils.is_standard_module'''
    def is_standard_module(self,modname, std_path=(STD_LIB_DIR,)):
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
        - is a built-in module"""
        modname = modname.split('.')[0]
        try:
            filename = file_from_modpath([modname])
        except ImportError, ex:
            # import failed, i'm probably not so wrong by supposing it's
            # not standard...
            print "Unresolved Import, module name - ", modname
            self.bad_imports += 1
            return 0
        # modules which are not living in a file are considered standard
        # (sys and __builtin__ for instance)
        self.good_imports += 1
        if filename is None:
            return 1
        filename = abspath(filename)
        for path in std_path:
            path = abspath(path)
            if filename.startswith(path):
                pfx_len = len(path)
                if filename[pfx_len + 1:pfx_len + 14] != 'site-packages':
                    return 1
                return 0
        return False



    def _imported_module(self, node, mod_path, relative):
        """notify an imported module, used to analyze dependencies
        """
        module = node.root()
        context_name = module.name
        if relative:
            mod_path = '%s.%s' % ('.'.join(context_name.split('.')[:-1]),
                                  mod_path)
        '''Save fullname for target modules'''
        if(hasattr(node, 'full_modnames')):
            node.full_modnames.append(mod_path)
        else:
            node.full_modnames = [mod_path]
            
        if self.compute_module(context_name, mod_path):
            # handle dependencies
            if not hasattr(module, 'depends'):
                module.depends = []
            mod_paths = module.depends
            if not mod_path in mod_paths:
                mod_paths.append(mod_path)
    
    def link_imports(self,root_astng):
        if(isinstance(root_astng, Import)):
            self.visit_import(root_astng)
        elif(isinstance(root_astng, From)):
            self.visit_from(root_astng)
        elif(isinstance(root_astng, Module)):
            self.visit_module(root_astng)
        elif(isinstance(root_astng, Class)):
            self.visit_class(root_astng)
        for child in root_astng.get_children():
            self.link_imports(child)
        
    
    def visit_from(self, node):
        """visit an astng.From node
        
        resolve module dependencies
        """
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
                            self.from_modname_imports+=1;
                            node.modname_import = True;
                        fullname = mod_fullname
                    except ImportError:
                        print "Unresolved From -", node.as_string(),"File -",node.root().name,"Lineno - ",node.fromlineno 
                        self.bad_from_imports+=1
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

''' Check names in project, trying to resolve it and summarizing information'''
class NamesChecker():
    pass

def make_tree(root_xml,root_astng):
    ''' Create tag with name of node class'''
    current_xml_node = etree.Element(root_astng.__class__.__name__)
    ''' Init namespace for frames'''
    if(isinstance(root_astng, Module) or isinstance(root_astng, Class) or isinstance(root_astng, Function)):
        xml_namespace = etree.Element("Namespace")
        current_xml_node.append(xml_namespace)
        xml_unresolved = etree.Element("Unresolved")
        current_xml_node.append(xml_unresolved)
    '''Set parameters, related with position in source code'''
    if(isinstance(root_astng, Module)):
        '''Set number of source code lines in module'''
        current_xml_node.set("num_lines",str(root_astng.tolineno))
    else:
                if(hasattr(root_astng, 'fromlineno')):
                    current_xml_node.set("fromlineno",str(root_astng.fromlineno))
                if(hasattr(root_astng, 'tolineno')):
                    current_xml_node.set("tolineno",str(root_astng.tolineno))
                if(hasattr(root_astng, 'col_offset')):
                    current_xml_node.set("col_offset",str(root_astng.col_offset))
    if(isinstance(root_astng, Import)):
        for name in root_astng.names:
            sub = etree.Element("ImportName", name=name[0])
            if (name[1]):
                 sub.set("asname",name[1])
            current_xml_node.append(sub)
    elif(isinstance(root_astng, From)):
        current_xml_node.set("modname",root_astng.modname);
        for name in root_astng.names:
            sub = etree.Element("ImportName", name=name[0])
            if (name[1]):
                 sub.set("asname",name[1])
            current_xml_node.append(sub)
    elif(isinstance(root_astng, Module)):
        '''Set dependencies of module'''
        for depend in root_astng.depends:
            sub = etree.Element("Dependency", module=depend)
            current_xml_node.append(sub)
        current_xml_node.set("name",root_astng.name)
    #===========================================================================
    elif(isinstance(root_astng, AssName)):
        #print root_astng.statement(),root_astng.name
        #print root_astng.as_string()
        current_xml_node.set("name",root_astng.name)
    # elif(isinstance(root_astng, DelName)):
    #    ##What is it?
    #    current_xml_node.set("unknown","true")
    # elif(isinstance(root_astng, Arguments)):
    #    '''Represent format of arguments'''
    #    current_xml_node.set("format_args",root_astng.format_args())
    elif(isinstance(root_astng, AssAttr)):
        current_xml_node.set("attrname",root_astng.attrname)
        current_xml_node.set("expr",root_astng.expr.as_string())
    # elif(isinstance(root_astng, Assert)):
    #    #Type of assert (what is checked?). It may be just name or compare
    #    current_xml_node.set("class",root_astng.test.__class__.__name__)
    #    current_xml_node.set("test",root_astng.test.as_string())
    #    #current_xml_node.set("expr",root_astng.expr.as_string())
    #===========================================================================
    elif(isinstance(root_astng, Assign)):
        #Targets is list
        #current_xml_node.set("targets",str(root_astng.targets))
        current_xml_node.set("value",root_astng.value.as_string())
    #===========================================================================
    # elif(isinstance(root_astng, AugAssign)):
    #    #+= Assign
    #    current_xml_node.set("target",root_astng.target.as_string())
    #    current_xml_node.set("value",root_astng.value.as_string())
    # elif(isinstance(root_astng, Backquote)):
    #    # It is ` command call, but i heven't seen it yet
    #    current_xml_node.set("value",root_astng.value.as_string())
    # elif(isinstance(root_astng, BinOp)):
    #    # Binary operation % or >>, for example
    #    current_xml_node.set("op",root_astng.op)
    #    current_xml_node.set("left",root_astng.left.as_string())
    #    current_xml_node.set("right",root_astng.right.as_string())
    # elif(isinstance(root_astng, BoolOp)):
    #    #may be FIXME - is not beautiful
    #    str_val = ""
    #    for val in root_astng.values:
    #        str_val+= val.as_string()+',' 
    #    current_xml_node.set("op",root_astng.op)
    #    current_xml_node.set("values",str_val)
    # elif(isinstance(root_astng, Break)):
    #    #isn't very interesting
    #    pass
    elif(isinstance(root_astng, CallFunc)):
        #print root_astng.root(),root_astng.fromlineno,root_astng.func
        current_xml_node.set("type",str(root_astng.func.__class__.__name__))
    #===========================================================================
    elif(isinstance(root_astng, Class)):
        current_xml_node.set("name",root_astng.name)
        #print root_astng.locals_type, root_astng.implements, root_astng.instance_attrs_type
        #current_xml_node.set("func",str(root_astng.func))
    #===========================================================================
    # elif(isinstance(root_astng, Compare)):
    #    #0 of ops is operation, !=, for example
    #    #FIXME ops is list of tuples!!!!!
    #    #Compare operators can be combined, for example  a == b == c or 1 <= x <= 10.
    #    current_xml_node.set("op",str(root_astng.ops[0]))
    # elif(isinstance(root_astng, Comprehension)):
    #    pass
    #    #Way to create list much simplier, for example [3*x for x in vec]
    #    #FIXME How it can be displayed
    #    #print root_astng.root(),root_astng.fromlineno,root_astng.target, root_astng.iter, root_astng.ifs
    #    #current_xml_node.set("op",str(root_astng.ops[0]))
    elif(isinstance(root_astng, Const)):
        current_xml_node.set("type",root_astng.name)
        current_xml_node.text = str(root_astng.as_string())
    # elif(isinstance(root_astng, Continue)):
    #    pass
    # elif(isinstance(root_astng, Decorators)):
    #    pass
    #    #Decorator for function or method
    #    #FIXME
    #    #print root_astng.root(),root_astng.fromlineno,root_astng.nodes
    #    #current_xml_node.set("type",root_astng.name)
    # elif(isinstance(root_astng, DelAttr)):
    #    #FIXME
    #    pass
    #    #print root_astng.root(),root_astng.fromlineno,root_astng.expr
    #    #current_xml_node.set("type",root_astng.name)
    # elif(isinstance(root_astng, Delete)):
    #    #FIXME
    #    pass
    #    #print root_astng.root(),root_astng.fromlineno,root_astng.expr
    #    #current_xml_node.set("type",root_astng.name)
    # elif(isinstance(root_astng, Dict)):
    #    pass
    #    #print root_astng.root(),root_astng.fromlineno,root_astng.items
    #    #current_xml_node.set("type",root_astng.name)
    # elif(isinstance(root_astng, Discard)):
    #    pass
    #    #print root_astng.root(),root_astng.fromlineno,root_astng.value
    #    #current_xml_node.set("type",root_astng.name)
    # elif(isinstance(root_astng, ExceptHandler)):
    #    #print root_astng.type,root_astng.name,root_astng.body,root_astng.parent
    #    current_xml_node.set("type",root_astng.type.__class__.__name__)
    # elif(isinstance(root_astng, Exec)):
    #    #print root_astng.expr,root_astng.globals,root_astng.locals
    #    current_xml_node.set("expr_type",root_astng.expr.__class__.__name__)
    # elif(isinstance(root_astng, ExtSlice)):
    #    #L[::2]
    #    print root_astng.dims
    # elif(isinstance(root_astng, For)):
    #    #print root_astng.body,root_astng.iter,root_astng.target,root_astng.orelse
    #    current_xml_node.set("iter",root_astng.iter.__class__.__name__)
    #===========================================================================
    elif(isinstance(root_astng, Function)):
        #print root_astng.name,root_astng.locals
        current_xml_node.set("name", root_astng.name)
    #===========================================================================
    # elif(isinstance(root_astng, GenExpr)):
    #    #print root_astng.generators,root_astng.locals,root_astng.as_string()
    #    current_xml_node.set("elt_type", root_astng.elt.__class__.__name__)
    elif(isinstance(root_astng, Getattr)):
        current_xml_node.set("attrname", root_astng.attrname)
        current_xml_node.set("expr", root_astng.expr.as_string())
    elif(isinstance(root_astng, Global)):
        print root_astng.names, root_astng.root(), root_astng.fromlineno
        #current_xml_node.set("name", root_astng.name)
    # elif(isinstance(root_astng, If)):
    #    #print root_astng.test, root_astng.body, root_astng.orelse
    #    current_xml_node.set("test",root_astng.test.__class__.__name__)
    # elif(isinstance(root_astng, IfExp)):
    #    print root_astng.test, root_astng.body, root_astng.orelse
    #    #current_xml_node.set("test",root_astng.test.__class__.__name__)
    # elif(isinstance(root_astng, Index)):
    #    #print root_astng.value
    #    current_xml_node.set("value_type",root_astng.value.__class__.__name__)
    # elif(isinstance(root_astng, Keyword)):
    #    #print root_astng.value
    #    current_xml_node.set("value_type",root_astng.value.__class__.__name__)
    # elif(isinstance(root_astng, Lambda)):
    #    #print root_astng.type, root_astng.args,root_astng.locals,root_astng.body
    #    current_xml_node.set("type",root_astng.type)
    # elif(isinstance(root_astng, List)):
    #    #print root_astng.elts
    #    pass
    # elif(isinstance(root_astng, ListComp)):
    #    #print root_astng.elt, root_astng.generators
    #    current_xml_node.set("elt_type",root_astng.elt.__class__.__name__)
    # elif(isinstance(root_astng, Pass)):
    #     pass
    # elif(isinstance(root_astng, Print)):
    #    #print root_astng.dest,root_astng.values
    #    current_xml_node.set("dest_type",root_astng.dest.__class__.__name__)
    #===========================================================================
    elif(isinstance(root_astng, Project)):
        #print "Name - ",root_astng.name
        #print "Keys ",root_astng.keys
        #print "Items ",root_astng.items
        #print "Modules ", root_astng.modules
        #print "Has_key", root_astng.has_key
        #print "Values ",root_astng.values
        #print "Path ",root_astng.path
        #print "Locals ",root_astng.locals
        current_xml_node.set("name",root_astng.name)
        current_xml_node.set("path",root_astng.path)
    #===========================================================================
    # elif(isinstance(root_astng, Raise)):
    #    #print root_astng.type,root_astng.inst,root_astng.tback
    #    current_xml_node.set("type",root_astng.type.__class__.__name__)
    #    current_xml_node.set("inst_type",root_astng.inst.__class__.__name__)
    # elif(isinstance(root_astng, Return)):
    #    #print root_astng.value
    #    current_xml_node.set("value_type",root_astng.value.__class__.__name__)
    #    #current_xml_node.set("inst_type",root_astng.inst.__class__.__name__)
    # elif(isinstance(root_astng, Slice)):
    #    #print root_astng.lower, root_astng.upper, root_astng.step
    #    current_xml_node.set("lower_type",root_astng.lower.__class__.__name__)
    #    current_xml_node.set("upper_type",root_astng.upper.__class__.__name__)
    #    current_xml_node.set("step_type",root_astng.step.__class__.__name__)
    # elif(isinstance(root_astng, Subscript)):
    #    #print root_astng.value, root_astng.slice, root_astng.as_string()
    #    current_xml_node.set("value_type",root_astng.value.__class__.__name__)
    #    current_xml_node.set("slice_type",root_astng.slice.__class__.__name__)
    # elif(isinstance(root_astng, TryExcept)):
    #    pass
    #    #print root_astng.body, root_astng.handlers, root_astng.orelse
    # elif(isinstance(root_astng, TryFinally)):
    #    pass
    #    #print root_astng.body, root_astng.finalbody
    #    #current_xml_node.set("value_type",root_astng.value.__class__.__name__)
    #    #current_xml_node.set("slice_type",root_astng.slice.__class__.__name__)
    # elif(isinstance(root_astng, Tuple)):
    #    pass
    #    #print root_astng.elts
    # elif(isinstance(root_astng, UnaryOp)):
    #    #print root_astng.operand,root_astng.as_string()
    #    current_xml_node.set("operand_type",root_astng.operand.__class__.__name__)
    # elif(isinstance(root_astng, While)):
    #    #print root_astng.test,root_astng.body,root_astng.orelse
    #    current_xml_node.set("test_type",root_astng.test.__class__.__name__)
    # elif(isinstance(root_astng, With)):
    #    #print root_astng.expr,root_astng.vars,root_astng.body
    #    pass
    # elif(isinstance(root_astng, Yield)):
    #    #print root_astng.value
    #    current_xml_node.set("value_type",root_astng.value.__class__.__name__)
    elif(isinstance(root_astng, Name)):
                #===============================================================
                # for name in root_astng.namespace[key]:
                #    sub = etree.Element("Name")
                # sub.set("name",name)
                # sub.set("type",key)
                # xml_namespace.append(sub)
                #===============================================================
        current_xml_node.set("name", root_astng.name)
        lookup_result = root_astng.lookup(root_astng.name)
        current_xml_node.set("scope", lookup_result[0].__class__.__name__)
        for assign in lookup_result[1]:
            sub = etree.Element("Assignment")
            #sub.text = assign.statement().as_string()
            if(isinstance(assign, Class)):
                sub.set("type","class_name")
            elif(isinstance(assign, Function)):
                sub.set("type","function_name")
            elif(isinstance(assign, Import)):
                sub.set("type","mod_name")
                for name in assign.names:
                    subsub = etree.Element("ImportName", name=name[0])
                    if (name[1]):
                        subsub.set("asname",name[1]) 
                sub.append(subsub)
            elif(isinstance(assign, From)):
                sub.set("type","import_name")
            elif(isinstance(assign, AssName)):
                if(isinstance(assign.root(), Module)):
                    if(isinstance(assign.statement(), Function)):
                        sub.set("type","function_argument")
                    else:
                        sub.text = assign.statement().as_string()
                else:
                    sub.text = assign.as_string()
            else:
                print "#####################################"
                print root_astng.root(), root_astng.fromlineno, root_astng.name 
                print root_astng.statement().as_string()
                print assign
            current_xml_node.append(sub)
    #===========================================================================
    # else:
    #    print root_astng.__class__.__name__
    #===========================================================================
    for child in root_astng.get_children():
        make_tree(current_xml_node, child)
    '''Namespace'''
    if(isinstance(root_astng, Module) or isinstance(root_astng, Class) or isinstance(root_astng, Function)):
        '''Write namespace to XML namespace'''
        for key in root_astng.keys():
                sub = etree.Element("Name")
                sub.set("name",key)
                sub.text = str(root_astng[key])
                xml_namespace.append(sub)
        '''Write unresolved names to XML'''    
        #current_xml_node.set("unresolved", str(len(root_astng.unresolved)))
        #for name in root_astng.unresolved:
         #       sub = etree.Element("Name")
          #      sub.set("name",name)
           #     xml_unresolved.append(sub)
    if(isinstance(root_astng, Module)):
        #compare_namespaces(root_astng)
        '''current_xml_node.set("unresolved",str(len(root_astng.unresolved)))
        for name in root_astng.unresolved:
            sub = etree.Element("Name")
            sub.set("name",name)
            xml_unresolved.append(sub)'''
        pass
    root_xml.append(current_xml_node)

class MySimpleASTNGProcessor(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        