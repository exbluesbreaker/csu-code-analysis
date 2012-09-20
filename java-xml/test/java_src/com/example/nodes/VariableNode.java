package com.example.nodes;

import com.example.visitors.NodeVisitor;

public class VariableNode extends Node {

	public String name = "variable";
	
	@Override
	public void accept(NodeVisitor visitor) {
		visitor.visitVariable(this);
	}

}
