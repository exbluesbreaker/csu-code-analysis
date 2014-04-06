'''
Created on 02.03.2014

@author: bluesbreaker
'''

import re
from lxml import etree
from CSUStAn.astng.inspector import ClassIRLinker
from CSUStAn.cross.duck_typing import DuckTypeHandler 
from logilab.common.configuration import ConfigurationMixIn
from logilab.astng.manager import astng_wrapper, ASTNGManager
from pylint.pyreverse.utils import get_visibility
from pylint.pyreverse.main import OPTIONS
from pylint.pyreverse.utils import insert_default_options


class UCRBuilder(ConfigurationMixIn,DuckTypeHandler):
    # generate XML, describing classes of project
    
    options = OPTIONS
    
    # criteria for duck typing
    _criteria = None
    _out_file = None
    _project = None
    _good_gettatr = 0
    _bad_gettatr = 0
    # numbers of "ducks" in project (for complexity estimation)
    _all_ducks = 0
    # numbers of classes in project (for complexity estimation)
    _all_classes = 0
    _found_ducks = 0
    _prob_used_classes = None
    _dbg_assattr_parents = None 
    _list_attrs = [attr for attr in dir([]) if not re.search('\A(?!_)',attr)]
    _list_methods = [attr for attr in dir([]) if re.search('\A(?!_)',attr)]
    _dict_attrs = [attr for attr in dir({}) if not re.search('\A(?!_)',attr)]
    _dict_methods = [attr for attr in dir({}) if re.search('\A(?!_)',attr)]
    _tuple_attrs = [attr for attr in dir(()) if not re.search('\A(?!_)',attr)]
    _tuple_methods = [attr for attr in dir(()) if re.search('\A(?!_)',attr)]
    _attr_iteration_cycles = 0
    _treshold = None
    _add_value = None
    
    def __init__(self, args,criteria='default',out_file='test.xml',treshold=None,add_value=False):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        self._add_value = add_value
        self._project = args[0]
        self._treshold = treshold
        self._out_file = out_file
        self._criteria = criteria
        self._prob_used_classes = set([])
        self._dbg_assattr_parents = set([])
        insert_default_options()
        self.manager = ASTNGManager()
        self.register_options_provider(self.manager)
        args = self.load_command_line_configuration()
        self.run(args)
    
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
    
    def get_duck_signature(self,duck):
        if(duck['complex_type']):
            if duck.has_key('element_signature'):
                # search for class of element is needed
                return set(duck['element_signature']['attrs'].keys()),set(duck['element_signature']['methods'].keys())
        return set(duck['attrs'].keys()), set(duck['methods'].keys())

    def run(self, args):
        """checking arguments and run project"""
        if not args:
            print self.help()
            return
        project = self.manager.project_from_files(args, astng_wrapper)
        self.project = project
        linker = ClassIRLinker(project)
        linker.visit(project)
        bad_ducks = 0
        successes = 0
        ducks_num = len(list(linker.get_ducks()))
        count = 1
        dbg = set([])
        empty_ducks = 0
        """ Handle "duck" information and generate information about types """
        for current_class in linker.get_classes():
            for duck in current_class.cir_ducks.keys():
                print "Processing ", count, " duck of ",ducks_num
                count +=1
                duck_attrs, duck_methods = self.get_duck_signature(current_class.cir_ducks[duck])
                # ignore empty ducks
                if((not duck_attrs) and (not duck_methods)):
                    empty_ducks+=1
                    continue
                if not hasattr(current_class.cir_ducks[duck], 'complex_type'):
                    # if duck is not detected  as complex type on previous stage (according to [],{} etc. usage)
                    # we need to check its methods and fields
                    complex_type = self._check_complex_type(duck_attrs, duck_methods)
                    if(complex_type):
                        current_class.cir_ducks[duck]['complex_type'] = complex_type
                        self._found_ducks+=1
                        continue
                duck_found = False
                for field_candidate in linker.get_classes():
                    result = self.check_candidate(duck_attrs, duck_methods, field_candidate,self._criteria)
                    if(result):
                        current_class.cir_ducks[duck]['type'].append(field_candidate)
                        self._prob_used_classes |= set([field_candidate.cir_uid]) 
                    duck_found = result or duck_found
                      
                #check if duck not found at all
                if(not duck_found):
                    bad_ducks += 1
                else:
                    self._found_ducks+=1 
                    dbg.add(str(current_class)+duck)
#        empty_ducks = len(list(linker.get_empty_ducks()))  
        print len(dbg)
        print "Project - ",self._project        
        print "Duck typing criteria - ",self._criteria            
        print "Numbers of ducks: ", linker.get_ducks_count()
        print "Numbers of ducks with assignment in class: ", len(list(linker.get_assigned_ducks()))
        print "Numbers of ducks with complex type: ", len(list(linker.get_complex_ducks()))
        if(linker.get_ducks_count()!=empty_ducks):
            print "Found ducks: ",self._found_ducks, " percentage from non-empty ducks: ",round(100*float(self._found_ducks)/(linker.get_ducks_count()-empty_ducks),1), " %"
        if(linker.get_attrs_count()!=0):
            print "Numbers of all attributes in project: ", linker.get_attrs_count(), " percentage of found attrs: ",round(100*float(self._found_ducks)/linker.get_attrs_count(),1), " %"
        print "Numbers of classes: ",len(list(linker.get_classes()))
        if(len(list(linker.get_classes()))!=0):
            print "Probably used (as field) classes: ",len(self._prob_used_classes)," percentage: ",round(100*float(len(self._prob_used_classes))/len(list(linker.get_classes())),1), " %"
        
        # result XML generation
        mapper = {}
        root = etree.Element("Classes")
        for obj in linker.get_classes():
            self._all_classes +=1
            node = etree.Element("Class",name=obj.name,fromlineno=str(obj.fromlineno),col_offset=str(obj.col_offset),id=str(obj.cir_uid),label=obj.root().name)
            mapper[obj] = node
            root.append(node)
            for attrname in obj.cir_attrs:
                attr_node = etree.Element('Attr',name=attrname)
                mod_node = etree.Element('Modifier',name=get_visibility(attrname))
                attr_node.append(mod_node)
                node.append(attr_node)
                if(attrname in obj.cir_ducks):
                    if obj.cir_ducks[attrname]['complex_type']:
                        for prob_type in obj.cir_ducks[attrname]['type']:
                            attr_node.append(etree.Element('AggregatedType',name=str(obj.cir_ducks[attrname]['complex_type']),element_type=prob_type.name,element_id=str(prob_type.cir_uid)))
                    else:
                        for prob_type in obj.cir_ducks[attrname]['type']:
                            if(obj.cir_ducks[attrname].has_key('type_values')):
                                common_type_node = etree.Element('CommonType',
                                                                 name=prob_type.name,
                                                                 id=str(prob_type.cir_uid),
                                                                 type_value=str(obj.cir_ducks[attrname]['type_values'][prob_type.cir_uid]))
                            else:
                                common_type_node = etree.Element('CommonType',
                                                                 name=prob_type.name,
                                                                 id=str(prob_type.cir_uid))
                            attr_node.append(common_type_node)    
            for meth in linker.get_methods(obj):
                meth_node = etree.Element('Method',name=meth.name)
                meth_node.set("fromlineno",str(meth.fromlineno))
                meth_node.set("col_offset",str(meth.col_offset))
                mod_node = etree.Element('Modifier',name=get_visibility(meth.name))
                meth_node.append(mod_node)
                """ This is needed for some native libs(pyx) """
                if(meth.args.args == None):
                    continue
                for arg in meth.args.args:
                    # ignore self arg
                    if not arg.name == 'self':
                        meth_node.append(etree.Element('Arg',name=arg.name))
                node.append(meth_node)
        for rel in linker.get_inheritances():
            mapper[rel[0]].append(etree.Element('Parent',name=rel[1].name,id=str(rel[1].cir_uid)))
        print "Writing ", self._out_file
        f = open(self._out_file,'w')
        f.write(etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
