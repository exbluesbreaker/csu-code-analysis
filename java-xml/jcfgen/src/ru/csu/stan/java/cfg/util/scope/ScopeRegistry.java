package ru.csu.stan.java.cfg.util.scope;

import java.util.LinkedList;
import java.util.List;

/**
 * 
 * @author mz
 *
 */
public class ScopeRegistry {
	private List<VariableScope> scopes = new LinkedList<VariableScope>();
	private static ScopeRegistry instance = new ScopeRegistry();
	
	private ScopeRegistry(){}
	
	public static ScopeRegistry getInstance(){
		return instance;
	}
	
	public void addScope(VariableScope scope){
		scopes.add(scope);
	}
	
	public List<VariableScope> getScopes(){
		return scopes;
	}
	
	public VariableScope findScopeByClass(String className){
		for (VariableScope scope: scopes)
			if (className.equals(scope.getName()))
				return scope;
		return null;
	}
}
