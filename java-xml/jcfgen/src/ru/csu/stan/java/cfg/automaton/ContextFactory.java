package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.util.MethodRegistry;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.util.ImportRegistry;
import ru.csu.stan.java.classgen.util.PackageRegistry;

/**
 * 
 * @author mz
 *
 */
public class ContextFactory {
	
	private ContextFactory() {}
	
	public static IContext<Project> getContextState(String name){
		return null;
	}
	
	public static IContext<Project> getStartContext(Project root, MethodRegistry registry, ImportRegistry imports, PackageRegistry packages){
		return new ProjectContext(root, registry, imports, packages);
	}
	
}
