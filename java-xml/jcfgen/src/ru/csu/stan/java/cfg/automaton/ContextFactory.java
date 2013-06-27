package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.classgen.automaton.IContext;

public class ContextFactory {
	
	private ContextFactory() {}
	
	public static IContext<Object> getContextState(String name){
		return null;
	}
	
	public static IContext<Object> getStartContext(Object root){
		return new EmptyContext(root, null);
	}
	
}
