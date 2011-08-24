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
    elif(isinstance(root_astng, Assign)):
        current_xml_node.set("targets",str(root_astng.targets))
        current_xml_node.set("value",str(root_astng.value))
    elif(isinstance(root_astng, Const)):
        current_xml_node.set("type",root_astng.name)
        current_xml_node.text = str(root_astng.as_string())
    elif(isinstance(root_astng, CallFunc)):
        #root_astng.__class__.__name__
        print ####
        print root_astng.starargs
        print root_astng.args
        print root_astng.func.__class__.__name__
        print root_astng.kwargs
        current_xml_node.set("func",str(root_astng.func))
        #current_xml_node.text = str(root_astng.as_string())
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