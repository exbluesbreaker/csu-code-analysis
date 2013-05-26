package ru.csu.stan.java.classgen.handlers;

import ru.csu.stan.java.classgen.automaton.IContext;

/**
 * Интерфейс обработчика STAX-события.
 * Обрабатывает событие, используя контекст классов.
 * 
 * @author mz
 *
 */
public interface IStaxHandler<T> {

	/**
	 * Обработка STAX-события.
	 * @param context контекст классов (конечный автомат).
	 * @return измененный контекст классов.
	 */
	public IContext<T> handle(final IContext<T> context);
}
