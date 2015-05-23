package ru.csu.stan.java.classgen.handlers;

import ru.csu.stan.java.classgen.automaton.IContext;

/**
 * Обработчик STAX-события, не делающий ничего. Нужен для пропуска действий.
 * 
 * @author mz
 *
 */
public class NothingToDoHandler<T> implements IStaxHandler<T> {

	@Override
	public IContext<T> handle(final IContext<T> context) {
		return context;
	}

}
