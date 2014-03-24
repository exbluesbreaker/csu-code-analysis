package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.automaton.base.ContextBase;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.util.MethodRegistry;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
import ru.csu.stan.java.classgen.util.ImportRegistry;
import ru.csu.stan.java.classgen.util.PackageRegistry;

/**
 * 
 * @author mz
 *
 */
class ProjectContext extends ContextBase {

	ProjectContext(ContextBase previousState) {
		super(previousState);
	}
	
	ProjectContext(Project resultRoot, MethodRegistry registry, ImportRegistry imports, PackageRegistry packages){
		super(resultRoot, registry, imports, packages);
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {

	}

	@Override
	public void finish(String eventName) {

	}

    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName)
    {
        if ("compilation_unit".equals(eventName))
            return new CompilationUnitContext(this);
        else
            return this;
    }

    @Override
    public IContext<Project> getPreviousState(String eventName)
    {
        return this;
    }

}
