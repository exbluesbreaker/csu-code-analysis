package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.automaton.base.ContextBase;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;

/**
 * 
 * @author mz
 *
 */
public class MethodArgumentsContext extends ContextBase {

	protected MethodArgumentsContext(ContextBase previousState) {
		super(previousState);
	}

	@Override
	public IContext<Project> getPreviousState(String eventName) {
		if ("arguments".equals(eventName))
			return getUpperState();
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
