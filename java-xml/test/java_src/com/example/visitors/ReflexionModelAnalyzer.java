package com.example.visitors;

import com.example.nodes.AssignmentNode;
import com.example.nodes.ClassNode;
import com.example.nodes.VariableNode;

public class ReflexionModelAnalyzer extends NodeVisitor {

	public Object mapping;
	
	@Override
	public void visitClass(ClassNode node) {
		System.out.println("RM visited class!");
	}

	@Override
	public void visitAssignment(AssignmentNode node) {
		System.out.println("RM visited assignment!");
	}

	@Override
	public void visitVariable(VariableNode node) {
		System.out.println("RM visited variable!");
	}

}
