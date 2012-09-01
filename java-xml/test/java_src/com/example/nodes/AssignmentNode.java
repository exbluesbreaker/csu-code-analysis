package com.example.nodes;

import com.example.visitors.NodeVisitor;

public class AssignmentNode extends Node {

	public String name = "assignment";
	
	@Override
	public void accept(NodeVisitor visitor) {
		visitor.visitAssignment(this);
	}

}
