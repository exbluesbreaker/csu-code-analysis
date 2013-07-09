package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;

public class ContextFactory {
	
	private ContextFactory() {}
	
	public static IContext<Project> getContextState(String name){
		return null;
	}
	
	public static IContext<Project> getStartContext(Project root){
		return new ProjectContext(root, null);
	}
	
}
