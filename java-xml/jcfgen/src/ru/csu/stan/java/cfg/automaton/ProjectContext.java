package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;

/**
 * 
 * @author mz
 *
 */
class ProjectContext extends ContextBase {

	ProjectContext(Project resultRoot, ContextBase previousState) {
		super(resultRoot, previousState);
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
            return new CompilationUnitContext(getResultRoot(), this);
        else
            return this;
    }

    @Override
    public IContext<Project> getPreviousState(String eventName)
    {
        return this;
    }

}
