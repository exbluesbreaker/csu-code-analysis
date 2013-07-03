package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;

public abstract class ContextBase implements IContext<Project> {

	private Project resultRoot;
	private ContextBase previousState;
	
	ContextBase(Object resultRoot, ContextBase previousState) {
	}

	@Override
	public ContextBase getPreviousState(String eventName) {
		return previousState;
	}

	@Override
	public Project getResultRoot() {
		return resultRoot;
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		IContext<Project> result = ContextFactory.getContextState(eventName);
		if (result != null)
			return result;
		else
			return this;
	}

}
