'''
Created on 02.03.2014

@author: bluesbreaker
'''

import re
import os
from lxml import etree
from copy import deepcopy
from logilab.common.configuration import ConfigurationMixIn
from pylint.pyreverse.main import OPTIONS

class ClassIRHandler:
    # Process XML class IR
    _ucr_tree = None
    _classes = None
    _full_name_dict = None
    _id_dict = None
    def __init__(self, ucr_xml):
        self._ucr_tree = etree.parse(ucr_xml)
        self._classes = [node for node in self._ucr_tree.iter("Class")]
        self._full_name_dict = {}
        self._id_dict = {}
        for class_node in self._classes:
            if class_node.get("label") != None:
                self._full_name_dict[class_node.get("label")+'.'+class_node.get("name")] = class_node
            else:
                self._full_name_dict[class_node.get("name")] = class_node
            self._id_dict[class_node.get("id")] = class_node      
    def get_methods(self,node):
        return set([meth.get("name") for meth in node.iter("Method")])
    def handle_attrs(self,node):
        return set([attr.get("name") for attr in node.iter("Attr")])
    def get_attr(self,node, attrname):
        attrs = [attr for attr in node.iter("Attr") if (attr.get("name")==attrname)]
        if(len(attrs)==0):
            return None
        else:
            return attrs[0]
    def get_common_type_values(self,node, attrname, value_dict= None):
        if value_dict is None:
            value_dict = {}
        attr = self.get_attr(node, attrname)
        if attr is not None:
            for type in attr.iter("CommonType"):
                type_name = self._id_dict[type.get("id")].get("label")+'.'+self._id_dict[type.get("id")].get("name")
                if (value_dict.has_key(type_name)):
                    if value_dict[type_name] < type.get("type_value"):
                        # use maximum value in inheritance hierarchy
                        value_dict[type_name] = type.get("type_value")
                else:
                    value_dict[type_name] = type.get("type_value")
        for parent in self.get_parents(node):
            self.get_common_type_values(parent, attrname, value_dict)
        return value_dict
    def get_type(self,type_mark,node, attrname, type_set= None):
        if type_set is None:
            type_set = set([])
        attr = self.get_attr(node, attrname)
        if attr is not None:
            if(type_mark=="AggregatedType"):
                """ Return type of element"""
                type_set |= set([self._id_dict[type.get("element_id")].get("label")+'.'+self._id_dict[type.get("element_id")].get("name") for type in attr.iter(type_mark)])
            else:
                type_set |= set([self._id_dict[type.get("id")].get("label")+'.'+self._id_dict[type.get("id")].get("name") for type in attr.iter(type_mark)])
        for parent in self.get_parents(node):
            self.get_type(type_mark,parent, attrname, type_set)
        return type_set
    def get_parents(self,node):
        return [self._ucr_tree.xpath("//Class[@id="+parent.get("id")+"]")[0] for parent in node.iter("Parent")]
    def get_all_parents(self,node,result=None):
        if(result is None):
            result = set([])
        parents = [self._ucr_tree.xpath("//Class[@id="+parent.get("id")+"]")[0] for parent in node.iter("Parent")]
        result|= set(parents)
        for p in parents:
            result = self.get_all_parents(p, result)
        return result
    def get_class_by_full_name(self,full_name):
        if self._full_name_dict.has_key(full_name):
            return self._full_name_dict[full_name]
        else: 
            print "None get_class_by_full_name", full_name
            return None
    def get_class_by_id(self,class_id):
        if self._id_dict.has_key(class_id):
            return self._id_dict[class_id]
        else: 
            return None
    def get_classes_from_module(self,modname):
        return self._ucr_tree.xpath("//Class[@label=\""+modname+"\"]")
    def get_num_of_classes(self):
        return len(self._classes)
    
    def for_each_class(self, function):
        for c in self._classes:
            function(c)
            
class FieldCandidateFinder(ConfigurationMixIn,ClassIRHandler):
    ''' scan classes description for candidate for class's field (deprecated, moved to ClassIRRunner) '''
    
    options = OPTIONS
    _successes = 0
    _fails = 0
    _ucr_tree = None
    _complete_signatures = None
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        ClassIRHandler.__init__(self, args[0])
        _complete_signatures = {}
        self.run(args)
        
    def _compute_signature(self,id,curr_node=None):
        if(curr_node is None):
            curr_node = self._ucr_tree.xpath("//Class[@id="+id+"]")[0]
        self._complete_signatures[id]['Attrs'] |= set([re.search('[^ :]*',attr.get("name")).group(0) for attr in curr_node.iter("Attr")])
        self._complete_signatures[id]['Methods'] |= self.get_methods(curr_node)
        parents = self.get_parents(curr_node)
        for parent in parents:
            self._compute_signature(id,parent)

    def run(self, args):
        ducks = [node for node in self._ucr_tree.iter("DuckAttr")]
        # prepare data about classes attrs and methods
        status = 0
        classes_num = len(self._classes)
        for node in self._classes:
            status +=1
            print "Complete ",status,"/",classes_num," class signatures"
            # ProbUsed will be true, if this class will be detect as candidate for duck field
            self._complete_signatures[node.get("id")]={'Attrs':set([]),'Methods':set([]),'ProbUsed' : False}
            self._compute_signature(node.get("id"))
        status = 0
        found_ducks = 0
        ducks_num = len(ducks)
        for duck in ducks:
            status +=1
            print "Complete ",status,"/",ducks_num," ducks" 
            duck_attrs = [node.get('name') for node in duck.iter("ProbAttr")]
            duck_methods = [node.get('name') for node in duck.iter("ProbMethod")]
            # ignore empty ducks
            if((not duck_attrs) and (not duck_methods)):
                continue
            max_matches = 0
            duck_found = False
            for id in self._complete_signatures.keys():
                if(all(attr in self._complete_signatures[id]['Attrs'] for attr in duck_attrs) and all(method in self._complete_signatures[id]['Methods'] for method in duck_methods)):
                    self._successes += 1
                    if(not duck_found):
                        found_ducks+=1
                        duck_found = True
                    self._complete_signatures[id]['ProbUsed']=True
                num_matches = sum(attr in self._complete_signatures[id]['Attrs'] for attr in duck_attrs)+sum(method in self._complete_signatures[id]['Methods'] for method in duck_methods)
                if(num_matches >  max_matches):
                    max_matches = num_matches
            #print "Max matches - ",max_matches," from ",len(duck_attrs)+len(duck_methods)
        prob_used_classes = 0
        for id in self._complete_signatures.keys():
            if  self._complete_signatures[id]['ProbUsed']== True:
                prob_used_classes+=1
        print "Numbers of ducks: ",len(ducks)
        print "Found ducks: ",found_ducks, " percentage: ",round(100*float(found_ducks)/len(ducks),1), " %"
        print "Numbers of classes: ",len(self._complete_signatures.keys())
        print "Probably used (as field) classes: ",prob_used_classes," percentage: ",round(100*float(prob_used_classes)/len(self._complete_signatures.keys()),1), " %"
        #for class_node in classes:
        
class TypesComparator(ClassIRHandler):
    
    #dictionary with information about types, got from running program
    _dynamic_types_info = None
    _result = None
    _result_file = None
    _project = None
    _preload_dt_info = None
    
    def __init__(self, class_ir_file,project,result_file=None):
        ClassIRHandler.__init__(self, class_ir_file)
        self._project = project
        self._result = {'not_found_common_types':0,'correct_common_types':0,'not_found_aggr_types':0,'correct_aggr_types':0}
        if result_file is not None:
            self._result_file = result_file
            self.preload_results()
        
    def compare_type_info(self,threshold=None):
        #Save result
        self.save_result()
        self._result = {'not_found_common_types':0,'correct_common_types':0,'not_found_aggr_types':0,'correct_aggr_types':0}
        for current_class in self._dynamic_types_info.keys():
            node = self.get_class_by_full_name(current_class)
            if node is None:
                    continue
            for attrname in self._dynamic_types_info[current_class][1].keys():
                common_type = self.get_type("CommonType",node,attrname)
                aggr_type = self.get_type("AggregatedType",node,attrname)
                for type in self._dynamic_types_info[current_class][1][attrname]['common_type']:
                    common_type_vals = self.get_common_type_values(node, attrname)
                    if type in common_type:
                        type_val = common_type_vals[type]
                        if((threshold is not None) and (type_val is not None)):
                            type_val = float(type_val)
                            if type_val >= threshold:
                                self._result['correct_common_types']+=1
                            else:
                                self._result['not_found_common_types']+=1
                        else:
                            #threshold will not be used
                            self._result['correct_common_types']+=1
                    else:
                        self._result['not_found_common_types']+=1
                for type in self._dynamic_types_info[current_class][1][attrname]['aggregated_type']:
                    if type in aggr_type:
                        self._result['correct_aggr_types']+=1
                    else:
                        self._result['not_found_aggr_types']+=1
    def save_result(self):
        if(self._result_file is not None):
            if(os.path.exists(self._result_file)):
                parser = etree.XMLParser(remove_blank_text=True)
                tree = etree.parse(self._result_file, parser)
                projects = [node for node in tree.getroot().iter("Project") if node.get("name")==self._project]
                for project in projects:
                    tree.getroot().remove(project)
                project = etree.Element("Project",name=self._project)
                tree.getroot().append(project)
                tree = tree.getroot()
            else:
                tree = etree.Element("DynamicResults")
                project = etree.Element("Project",name=self._project)
                tree.append(project)
            for c in self._dynamic_types_info.keys():
                c_node = etree.Element("Class",name=c)
                project.append(c_node)
                for attr in self._dynamic_types_info[c][1].keys():
                    a_node = etree.Element("Attr",name=attr)
                    c_node.append(a_node)
                    for ct in self._dynamic_types_info[c][1][attr]['common_type']:
                        ct_node = etree.Element("CommonType",name=ct)
                        a_node.append(ct_node)
                    for at in self._dynamic_types_info[c][1][attr]['aggregated_type']:
                        at_node = etree.Element("AggregatedType",name=at)
                        a_node.append(at_node)
            f = open(self._result_file,'w')
            f.write(etree.tostring(tree, pretty_print=True, encoding='utf-8', xml_declaration=True))
            f.close()
    def preload_results(self):
        if(not os.path.exists(self._result_file)):
            self._preload_dt_info = {}
            return
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(self._result_file, parser)
        projects = [node for node in tree.getroot().iter("Project") if node.get("name")==self._project]
        if(projects is None):
            self._preload_dt_info = {}
            return
        dt_info = {}
        for project in projects:
            for c in project.iter("Class"):
                if not dt_info.has_key(c.get("name")):
                    dt_info[c.get("name")] = [0, {}]
                for attr in c.iter("Attr"):
                    if not dt_info[c.get("name")][1].has_key(attr.get("name")):
                        dt_info[c.get("name")][1][attr.get("name")]={'common_type':set([]),'aggregated_type':set([])}
                    for ct in attr.iter("CommonType"):
                        dt_info[c.get("name")][1][attr.get("name")]['common_type'].add(ct.get("name"))
                    for at in attr.iter("AggregatedType"):
                        dt_info[c.get("name")][1][attr.get("name")]['aggregated_type'].add(at.get("name")) 
        self._preload_dt_info = dt_info
             
            
    def get_result(self):
        return self._result.copy()
    
class PotentialSiblingsCounter(ConfigurationMixIn,ClassIRHandler):
    # search for probable inheritance mistakes
    
    options = OPTIONS
    _methods = None
    
    def __init__(self, args):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        ClassIRHandler.__init__(self, args[0])
        self._methods = {}
        self.run()
    
    def run(self):
        status = 0
        classes_num = len(self._classes)
        for node in self._classes:
            print "Complete ",status,"/",classes_num," classes"
            # ProbUsed will be true, if this class will be detect as candidate for duck field
            #self._complete_signatures[node.get("id")]={'Attrs':Set([]),'Methods':Set([]),'ProbUsed' : False}
            for method in self.get_methods(node):
                if self._assign_method(node,method):
                    if self._methods.has_key(method):
                        self._methods[method].append(node.get("id"))
                    else:
                        self._methods[method]=[node.get("id")]
            status +=1
        methods_num = len(self._methods.keys())
        status = 0
        count = 0
        for method in self._methods.keys():
            print "Complete ",status,"/",methods_num," method names"
            if(len(self._methods[method])>1):
                print "Method ",method," implemented in classes(id): ",self._methods[method]
                count+=1
            status +=1
        print count," method names of ",methods_num,"unique method names in project pretend to to be passed to common superclass"
                
                
    def _assign_method(self,node,method,main=True):
        if((not main) and (method in self.get_methods(node))):
            return False
        for parent in self.get_parents(node):
            if(not self._assign_method(parent, method, False)):
                return False            
        return True

class UCRSlicer(ClassIRHandler):
    ''' Abstract UCR slicer '''
    _sliced_classes = set([])
    _out_file = None
    
    def __init__(self, in_file):
        ClassIRHandler.__init__(self, in_file)
        
        
    def slice_ucr(self):
        self.slice()
        return self.extract_slicing()
        
    def write_slicing(self,out_file, root_node):
        f = open(out_file,'w')
        f.write(etree.tostring(root_node, pretty_print=True, encoding='utf-8', xml_declaration=True))
        f.close()
        
    def extract_slicing(self):
        root_node = etree.Element("Classes")
        for c in self._sliced_classes:
            root_node.append(deepcopy(c))
        return root_node
    
class InheritanceSlicer(ConfigurationMixIn,UCRSlicer):
    ''' Slice given class and all inheritance-related classes '''
    
    options = OPTIONS
    _methods = None
    _class_id = None
    
    def __init__(self, in_file,out_file, class_id):
        ConfigurationMixIn.__init__(self, usage=__doc__)
        UCRSlicer.__init__(self, in_file)
        self._methods = {}
        self._class_id = class_id
        root_node = self.slice_ucr()
        self.write_slicing(out_file,root_node)
        
    def slice(self):
        self.slice_class(self._id_dict[self._class_id])
        
    def slice_class(self,node):
        self._sliced_classes.add(node)
        for p in self.get_parents(node):
            self.slice_class(p)
