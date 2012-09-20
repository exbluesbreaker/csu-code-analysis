package com.example.visitors;

import com.example.nodes.AssignmentNode;
import com.example.nodes.ClassNode;
import com.example.nodes.VariableNode;

public abstract class NodeVisitor {
	public abstract void visitClass(ClassNode node);
	public abstract void visitAssignment(AssignmentNode node);
	public abstract void visitVariable(VariableNode node);
}
