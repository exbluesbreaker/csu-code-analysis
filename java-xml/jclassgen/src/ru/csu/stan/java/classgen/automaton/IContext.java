package ru.csu.stan.java.classgen.automaton;

import ru.csu.stan.java.classgen.handlers.NodeAttributes;


public interface IContext<T> {

	IContext<T> getPreviousState(String eventName);
	
	IContext<T> getNextState(IContext<T> context, String eventName);
	
	void processTag(String name, NodeAttributes attrs);
	
	void finish(String eventName);
	
	T getResultRoot();
}
