package ru.csu.stan.java.cfg.automaton;

import java.util.Iterator;

import javax.xml.stream.events.Attribute;

class ProjectContext extends ContextBase {

	ProjectContext(Object resultRoot, ContextBase previousState) {
		super(resultRoot, previousState);
	}

	@Override
	public void processTag(String name, Iterator<Attribute> attrs) {

	}

	@Override
	public void finish(String eventName) {

	}

}
