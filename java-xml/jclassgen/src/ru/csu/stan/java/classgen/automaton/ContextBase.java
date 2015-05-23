package ru.csu.stan.java.classgen.automaton;

import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.jaxb.ObjectFactory;

abstract class ContextBase implements IContext<Classes> {

	protected Classes root;
	protected ObjectFactory factory;

}
