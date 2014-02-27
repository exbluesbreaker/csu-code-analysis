package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;

/**
 * 
 * @author mz
 *
 */
public class VariableContext extends ContextBase {

	VariableContext(Project resultRoot, ContextBase previousState) {
		super(resultRoot, previousState);
	}

	@Override
	public IContext<Project> getPreviousState(String eventName) {
		if ("variable".equals(eventName))
			return getPreviousState();
		else
			return this;
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		return null;
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {

	}

	@Override
	public void finish(String eventName) {

	}

}
