
class NodeVisitor:
    
    def visit_class(self, node):
        pass
    
    def visit_assignment(self, node):
        pass
    
    def visit_variable(self, node):
        pass
    
class ReflexionModelAnalyzer(NodeVisitor):
    
    mapping = None
    
    def visit_class(self, node):
        print "RM visited class!"
        
    def visit_assignment(self, node):
        print "RM visited assignment!"
        
    def visit_variable(self, node):
        print "RM visited variable!"
        
class Verificator(NodeVisitor):
    
    specification = None
    
    def visit_class(self, node):
        print "Verifying class!"
        
    def visit_assignment(self, node):
        print "Verifying assignment!"
        
    def visit_variable(self, node):
        print "Verifying variable!"
