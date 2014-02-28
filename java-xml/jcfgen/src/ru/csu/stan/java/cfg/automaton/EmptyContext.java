package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;

/**
 * Пустое состояние. Ничего не делает.
 * 
 * @author mz
 *
 */
class EmptyContext extends ContextBase {

	EmptyContext(ContextBase previousState) {
		super(previousState);
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		return ContextFactory.getContextState(eventName);
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {

	}

	@Override
	public void finish(String eventName) {

	}

    @Override
    public IContext<Project> getPreviousState(String eventName)
    {
        return getPreviousState();
    }

}
