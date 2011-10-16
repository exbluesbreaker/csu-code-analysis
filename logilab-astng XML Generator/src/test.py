# -*- coding: utf-8 -*-
'''
Created on 19.08.2011

@author: bluesbreaker
'''
import logilab.astng
from logilab.common.configuration import ConfigurationMixIn
from pylint.pyreverse.utils import insert_default_options
from logilab.astng.inspector import Linker
from pylint.pyreverse.diadefslib import DiadefsHandler
from pylint.pyreverse import writer
from lxml import etree
from logilab.astng import builder
'''import all names of nodes'''
from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import *
from logilab.astng.manager import astng_wrapper, ASTNGManager
from logilab.astng.manager import Project
from pylint.pyreverse.main import PyreverseCommand
from logilab.common.modutils import get_module_part, is_relative, \
     is_standard_module


 
if __name__ == '__main__':
    pass

main_prj = None



def write_to_namespace(node, names,type):
    if(hasattr(node, "namespace")):
        if(isinstance(names, list)):
            for name in names:
                if(not name in node.namespace[type]):
                    '''Unknown name now resolved(import)'''
                    if((type != 'unknown') and (name in node.namespace['unknown'])):
                        node.namespace['unknown'].remove(name)
                    node.namespace[type].append(name)
        else:
            if(not names in node.namespace[type]):
                '''Unknown name now resolved(import)'''
                if((type != 'unknown') and (names in node.namespace['unknown'])):
                    node.namespace['unknown'].remove(names)
                node.namespace[type].append(names)

''' Init namespaces, make local namespaces for modules and make local resolving '''
def make_local_namespaces(root_astng):
    if(isinstance(root_astng, Module)):
        if(hasattr(root_astng, 'namespace')):
            print "Error Node Module allready have namespace"
        else:
            root_astng.namespace = {'locals':[],'unknown': [],'imports':[]}
            root_astng.unresolved = []
    elif(isinstance(root_astng, Assign)):
        for target in root_astng.targets:
            if(isinstance(target, AssName)):
                '''ROOT?'''
                write_to_namespace(root_astng.frame(), (target.name,'vars'),'unknown')
    elif(isinstance(root_astng, Class)):
        ''' Frame for class is class itself'''
        write_to_namespace(root_astng.parent.frame(), (root_astng.name,'class'),'locals')
        if(hasattr(root_astng, 'namespace')):
            print "Error Node Class allready have namespace"
        else:
            root_astng.namespace = {'locals':[],'unknown': [],'imports':[]}
            root_astng.unresolved = []
    elif(isinstance(root_astng, Function)):
        ''' Frame for func is func itself'''
        write_to_namespace(root_astng.parent.frame(), (root_astng.name,'func'),'locals')
        if(hasattr(root_astng, 'namespace')):
            print "Error Node Function allready have namespace"
        else:
            root_astng.namespace = {'locals':[],'unknown': [],'imports':[]}
            root_astng.unresolved = []
    elif(isinstance(root_astng, Lambda)):
        #write_to_namespace(root_astng.frame(), (root_astng.name,'lambda'),'locals')
        if(hasattr(root_astng, 'namespace')):
            print "Error Node Lambda allready have namespace"
        else:
            root_astng.namespace = {'locals':[],'unknown': [],'imports':[]}
            root_astng.unresolved = []
    elif(isinstance(root_astng, Name)):
        ''' For NodeNG frame returns first parent frame node(module, class, func)!'''
        '''FIXME func arguments is not unresolved!!!'''
        if(hasattr(root_astng.frame(), "namespace")):
            for key in root_astng.frame().namespace.keys():
                    try:
                        namespace_name = root_astng.frame().namespace[key].index(root_astng.name)
                        root_astng.name_type = namespace_name[1]
                        root_astng.name_source = key
                    except ValueError:
                        continue
    for child in root_astng.get_children():
        make_local_namespaces(child)
        
''' Make namespaces for modules and make resolving '''
def make_namespaces(root_astng):
    #if(hasattr(root_astng, "full_modname")):
     #   if(main_prj.locals.has_key(root_astng.full_modname)):
      #      print root_astng.full_modname
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
                        write_to_namespace(root_astng.frame(), target_module.namespace['locals'],'imports')
                        write_to_namespace(root_astng.frame(), target_module.namespace['unknown'],'imports')
                    else:
                        for key in target_module.namespace.keys():
                            for target_name in target_module.namespace[key]:
                                if(name[0]==target_name[0]):
                                    ''' name[1] is asname '''
                                    if(name[1]):
                                        write_to_namespace(root_astng.frame(), name[1],'imports')
                                    else:
                                        write_to_namespace(root_astng.frame(), name[0],'imports')
                except KeyError:
                    pass
                    #root_astng.root.unresolved +=1
            '''FIXME import module name not name in module'''
            #if (name[1]):
             #   write_to_namespace(root_astng.parent, (name[1],'mod_name'),'imports')
            #else:
             #   write_to_namespace(root_astng.parent, (name[0],'mod_name'),'imports')
    elif(isinstance(root_astng, Name)):
        '''If name allready resolved'''
        if(not hasattr(root_astng, "name_type")):
            if(hasattr(root_astng.frame(), "namespace")):
                for key in root_astng.frame().namespace.keys():
                    for target_name in root_astng.frame().namespace[key]:
                        if(root_astng.name==target_name[0]):
                            root_astng.name_type = target_name[1]
                            root_astng.name_source = key
        if(not hasattr(root_astng, "name_type")):
            if(not root_astng.name in root_astng.frame().unresolved):
                root_astng.frame().unresolved.append(root_astng.name) # name is not in namespace
    for child in root_astng.get_children():
        make_namespaces(child)
        
def make_tree(root_xml,root_astng):
    ''' Create tag with name of node class'''
    current_xml_node = etree.Element(root_astng.__class__.__name__)
    '''Set parameters, related with position in source code'''
    if(isinstance(root_astng, Module)):
        '''Set number of source code lines in module'''
        current_xml_node.set("num_lines",str(root_astng.tolineno))
        ''' Init namespace for module'''
        xml_namespace = etree.Element("Namespace")
        current_xml_node.append(xml_namespace)
        xml_unresolved = etree.Element("Unresolved")
        current_xml_node.append(xml_unresolved)
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
    # elif(isinstance(root_astng, AssName)):
    #    current_xml_node.set("name",root_astng.name)
    # elif(isinstance(root_astng, DelName)):
    #    ##What is it?
    #    current_xml_node.set("unknown","true")
    # elif(isinstance(root_astng, Arguments)):
    #    '''Represent format of arguments'''
    #    current_xml_node.set("format_args",root_astng.format_args())
    # elif(isinstance(root_astng, AssAttr)):
    #    current_xml_node.set("attrname",root_astng.attrname)
    #    current_xml_node.set("expr",root_astng.expr.as_string())
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
        ''' Namespace '''
        for target in root_astng.targets:
            if(isinstance(target, AssName)):
                write_to_namespace(root_astng.parent, (target.name,'vars'),'locals')
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
    # elif(isinstance(root_astng, CallFunc)):
    #    #print root_astng.root(),root_astng.fromlineno,root_astng.func
    #    current_xml_node.set("type",str(root_astng.func.__class__.__name__))
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
    # elif(isinstance(root_astng, Const)):
    #    current_xml_node.set("type",root_astng.name)
    #    current_xml_node.text = str(root_astng.as_string())
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
    # elif(isinstance(root_astng, Getattr)):
    #    current_xml_node.set("attrname", root_astng.attrname)
    #    current_xml_node.set("expr", root_astng.expr.as_string())
    # elif(isinstance(root_astng, Global)):
    #    pass
    #    #print root_astng.names, root_astng.root(), root_astng.fromlineno
    #    #current_xml_node.set("name", root_astng.name)
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
        if(hasattr(root_astng, "name_type")):
            current_xml_node.set("type", root_astng.name_type)            
            current_xml_node.set("source", root_astng.name_source)
        else:
            current_xml_node.set("source", "unknown")
    #===========================================================================
    # else:
    #    print root_astng.__class__.__name__
    #===========================================================================
    for child in root_astng.get_children():
        make_tree(current_xml_node, child)
    '''Namespace'''
    if(isinstance(root_astng, Module)):
        '''Write namespace to XML namespace'''
        for key in root_astng.namespace.keys():
            xml_source = etree.Element(key)
            for name in root_astng.namespace[key]:
                sub = etree.Element("Name")
                sub.set("name",name[0])
                sub.set("type",name[1])
                xml_source.append(sub)
            xml_namespace.append(xml_source)
        '''Write namespace to XML unresolved'''
        current_xml_node.set("unresolved", str(len(root_astng.unresolved)))
        for name in root_astng.unresolved:
                sub = etree.Element("Name")
                sub.set("name",name)
                xml_unresolved.append(sub)
    root_xml.append(current_xml_node)
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

class MyLogilabLinker(Linker):
    def _imported_module(self, node, mod_path, relative):
        """notify an imported module, used to analyze dependencies
        """
        module = node.root()
        context_name = module.name
        if relative:
            mod_path = '%s.%s' % ('.'.join(context_name.split('.')[:-1]),
                                  mod_path)
        if self.compute_module(context_name, mod_path):
            # handle dependencies
            if not hasattr(module, 'depends'):
                module.depends = []
            mod_paths = module.depends
            node.full_modname = mod_path
            if not mod_path in mod_paths:
                mod_paths.append(mod_path)
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
                        fullname = get_module_part(fullname)
                    except ImportError:
                        continue
            self._imported_module(node, fullname, relative)

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
        """handler = DiadefsHandler(self.config)
        diadefs = handler.get_diadefs(project, linker)
        if self.config.output_format == "vcg":
            writer.VCGWriter(self.config).write(diadefs)
        else:
            writer.DotWriter(self.config).write(diadefs)"""    

pc = LogilabXMLGenerator(sys.argv[1:])
xml_root = etree.Element("PythonSourceTree")
main_prj = pc.project
make_local_namespaces(pc.project)
make_namespaces(pc.project)
make_tree(xml_root,pc.project)
handle = etree.tostring(xml_root, pretty_print=True, encoding='utf-8', xml_declaration=True)       
applic = open(sys.argv[-1], "w")
applic.writelines(handle)
applic.close()