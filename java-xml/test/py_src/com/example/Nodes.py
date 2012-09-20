
class Node:
    lineno = 0
    strPos = 0
    
    def accept(self, visitor):
        pass
    
class ClassNode(Node):
    name = "class"
    
    def accept(self, visitor):
        visitor.visit_class(self)
        
class AssignmentNode(Node):
    name = "assignment"
    
    def accept(self, visitor):
        visitor.visit_assignment(self)
        
class VariableNode(Node):
    name = "variable"
    
    def accept(self, visitor):
        visitor.visit_variable(self)
