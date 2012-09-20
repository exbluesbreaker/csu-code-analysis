package com.example.nodes;

import com.example.visitors.NodeVisitor;

public class ClassNode extends Node {

	public String name = "class";
	
	@Override
	public void accept(NodeVisitor visitor) {
		visitor.visitClass(this);
	}

}
