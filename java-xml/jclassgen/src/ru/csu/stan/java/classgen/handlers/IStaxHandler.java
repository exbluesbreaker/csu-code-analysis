package ru.csu.stan.java.classgen.handlers;

import ru.csu.stan.java.classgen.util.ClassContext;

/**
 * Интерфейс обработчика STAX-события.
 * Обрабатывает событие, используя контекст классов.
 * 
 * @author mz
 *
 */
public interface IStaxHandler {

	/**
	 * Обработка STAX-события.
	 * @param context контекст классов (конечный автомат).
	 * @return измененный контекст классов.
	 */
	public ClassContext handle(final ClassContext context);
}
