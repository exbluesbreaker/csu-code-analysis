package ru.csu.stan.java.cfg.automaton;

import java.util.Iterator;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;

class EmptyContext extends ContextBase {

	EmptyContext(Object resultRoot, ContextBase previousState) {
		super(resultRoot, previousState);
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		return ContextFactory.getContextState(eventName);
	}

	@Override
	public void processTag(String name, Iterator<Attribute> attrs) {

	}

	@Override
	public void finish(String eventName) {

	}

}
