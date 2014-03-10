package ru.csu.stan.java.cfg.util.scope;

import java.util.HashSet;
import java.util.Set;

/**
 * 
 * @author mz
 *
 */
public class VariableScope {
	private Set<VariableFromScope> vars = new HashSet<VariableFromScope>();
	
	public Set<VariableFromScope> listVars(){
		return vars;
	}
	
	public void addVar(VariableFromScope variable){
		vars.add(variable);
	}
}
