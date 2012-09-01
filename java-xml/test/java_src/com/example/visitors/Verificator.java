package com.example.visitors;

import com.example.nodes.AssignmentNode;
import com.example.nodes.ClassNode;
import com.example.nodes.VariableNode;

public class Verificator extends NodeVisitor {

	public Object specification;
	
	@Override
	public void visitClass(ClassNode node) {
		System.out.println("Verifying class!");
	}

	@Override
	public void visitAssignment(AssignmentNode node) {
		System.out.println("Verifying assignment!");
	}

	@Override
	public void visitVariable(VariableNode node) {
		System.out.println("Verifying variable!");
	}

}
