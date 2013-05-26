package ru.csu.stan.java.classgen.automaton;

import java.util.Iterator;

import javax.xml.stream.events.Attribute;


public interface IContext<T> {

	IContext<T> getPreviousState(String eventName);
	
	IContext<T> getNextState(IContext<T> context, String eventName);
	
	void processTag(String name, Iterator<Attribute> attrs);
	
	void finish(String eventName);
	
	T getResultRoot();
}
