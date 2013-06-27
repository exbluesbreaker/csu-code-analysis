package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.classgen.automaton.IContext;

public abstract class ContextBase implements IContext<Object> {

	private Object resultRoot;
	private ContextBase previousState;
	
	ContextBase(Object resultRoot, ContextBase previousState) {
	}

	@Override
	public ContextBase getPreviousState(String eventName) {
		return previousState;
	}

	@Override
	public Object getResultRoot() {
		return resultRoot;
	}

	@Override
	public IContext<Object> getNextState(IContext<Object> context, String eventName) {
		IContext<Object> result = ContextFactory.getContextState(eventName);
		if (result != null)
			return result;
		else
			return this;
	}

}
