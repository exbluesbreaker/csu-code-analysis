package ru.csu.stan.java.classgen.handlers;

import ru.csu.stan.java.classgen.util.ClassContext;

public class NothingToDoHandler implements IStaxHandler {

	@Override
	public ClassContext handle(final ClassContext context) {
		return context;
	}

}
