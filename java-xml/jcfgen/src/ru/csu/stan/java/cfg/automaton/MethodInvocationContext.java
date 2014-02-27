package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;

/**
 * 
 * @author mz
 *
 */
public class MethodInvocationContext extends ContextBase {

	MethodInvocationContext(Project resultRoot, ContextBase previousState) {
		super(resultRoot, previousState);
	}

	@Override
	public IContext<Project> getPreviousState(String eventName) {
		if ("method_invocation".equals(eventName))
			return getPreviousState();
		else
			return this;
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		return this;
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {

	}

	@Override
	public void finish(String eventName) {

	}

}
