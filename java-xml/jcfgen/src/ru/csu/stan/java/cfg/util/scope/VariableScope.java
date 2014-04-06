package ru.csu.stan.java.cfg.util.scope;

import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;

/**
 * 
 * @author mz
 *
 */
public class VariableScope {
	private List<VariableScope> children = new LinkedList<VariableScope>();
	private Set<VariableFromScope> vars = new HashSet<VariableFromScope>();
	private String name;
	
	public void setParentScope(VariableScope parent){
		parent.addChild(this);
	}
	
	public void addChild(VariableScope scope){
		this.children.add(scope);
	}
	
	public List<VariableScope> listChildren(){
		return children;
	}
	
	public Set<VariableFromScope> listVars(){
		return vars;
	}
	
	public void addVar(VariableFromScope variable){
		vars.add(variable);
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}
	
	public VariableScope findScopeInChildren(String name){
		for (VariableScope child: children)
			if (name.equals(child.getName()))
				return child;
		return null;
	}
}
