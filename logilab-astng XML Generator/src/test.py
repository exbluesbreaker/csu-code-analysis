# -*- coding: utf-8 -*-
'''
Created on 19.08.2011

@author: bluesbreaker
'''
import logilab.astng
from lxml import etree
from logilab.astng import builder
'''import all names of nodes'''
from logilab.astng.node_classes import *
from logilab.astng.scoped_nodes import *
from logilab.astng.manager import astng_wrapper, ASTNGManager
from pylint.pyreverse.main import PyreverseCommand
 
if __name__ == '__main__':
    pass

def make_tree(root_xml,root_astng):
    ''' Create tag with name of node class'''
    current_xml_node = etree.Element(root_astng.__class__.__name__)
    '''If node, related with position in text file'''
    if(hasattr(root_astng, 'fromlineno')):
        '''FIXME Module doesn't need it''' 
        current_xml_node.set("fromlineno",str(root_astng.fromlineno))
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
        current_xml_node.set("name",root_astng.name)
    elif(isinstance(root_astng, AssName)):
        current_xml_node.set("name",root_astng.name)
    elif(isinstance(root_astng, DelName)):
        ##What is it?
        current_xml_node.set("unknown","true")
    elif(isinstance(root_astng, Arguments)):
        '''Represent format of arguments'''
        current_xml_node.set("format_args",root_astng.format_args())
    elif(isinstance(root_astng, AssAttr)):
        current_xml_node.set("attrname",root_astng.attrname)
        current_xml_node.set("expr",root_astng.expr.as_string())
    elif(isinstance(root_astng, Assert)):
        #Type of assert (what is checked?). It may be just name or compare
        current_xml_node.set("class",root_astng.test.__class__.__name__)
        current_xml_node.set("test",root_astng.test.as_string())
        #current_xml_node.set("expr",root_astng.expr.as_string())
    elif(isinstance(root_astng, Assign)):
        #FIXME better targets
        current_xml_node.set("targets",str(root_astng.targets))
        current_xml_node.set("value",root_astng.value.as_string())
    elif(isinstance(root_astng, AugAssign)):
        #+= Assign
        current_xml_node.set("target",root_astng.target.as_string())
        current_xml_node.set("value",root_astng.value.as_string())
    elif(isinstance(root_astng, Backquote)):
        # It is ` command call, but i heven't seen it yet
        current_xml_node.set("value",root_astng.value.as_string())
    elif(isinstance(root_astng, BinOp)):
        # Binary operation % or >>, for example
        current_xml_node.set("op",root_astng.op)
        current_xml_node.set("left",root_astng.left.as_string())
        current_xml_node.set("right",root_astng.right.as_string())
    elif(isinstance(root_astng, BoolOp)):
        #may be FIXME - is not beautiful
        str_val = ""
        for val in root_astng.values:
            str_val+= val.as_string()+',' 
        current_xml_node.set("op",root_astng.op)
        current_xml_node.set("values",str_val)
    elif(isinstance(root_astng, Break)):
        #isn't very interesting
        pass
    elif(isinstance(root_astng, CallFunc)):
        current_xml_node.set("func",str(root_astng.func))
    elif(isinstance(root_astng, Compare)):
        #0 of ops is operation, !=, for example
        #FIXME ops is lisr of tuples!!!!!
        current_xml_node.set("op",str(root_astng.ops[0]))
    elif(isinstance(root_astng, Const)):
        current_xml_node.set("type",root_astng.name)
        current_xml_node.text = str(root_astng.as_string())
    elif(isinstance(root_astng, Name)):
        current_xml_node.set("name", root_astng.name)
    elif(isinstance(root_astng, Getattr)):
        current_xml_node.set("attrname", root_astng.attrname)
        current_xml_node.set("expr", root_astng.expr.as_string())
    root_xml.append(current_xml_node)
    for child in root_astng.get_children():
        make_tree(current_xml_node, child)
    

pc = PyreverseCommand(sys.argv[1:])
xml_root = etree.Element("Project")
make_tree(xml_root,pc.project)
handle = etree.tostring(xml_root, pretty_print=True, encoding='utf-8', xml_declaration=True)       
applic = open("/home/bluesbreaker/test.xml", "w")
applic.writelines(handle)
applic.close()