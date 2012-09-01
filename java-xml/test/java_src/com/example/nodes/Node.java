package com.example.nodes;

import com.example.visitors.NodeVisitor;

public abstract class Node {
	public int lineno;
	public int strPos;
	
	public abstract void accept(NodeVisitor visitor);
}
