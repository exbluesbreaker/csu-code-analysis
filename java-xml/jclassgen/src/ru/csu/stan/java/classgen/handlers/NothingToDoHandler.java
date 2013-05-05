package ru.csu.stan.java.classgen.handlers;

import ru.csu.stan.java.classgen.automaton.ClassContext;

/**
 * Обработчик STAX-события, не делающий ничего. Нужен для пропуска действий.
 * 
 * @author mz
 *
 */
public class NothingToDoHandler implements IStaxHandler {

	@Override
	public ClassContext handle(final ClassContext context) {
		return context;
	}

}
