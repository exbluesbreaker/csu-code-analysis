package ru.csu.stan.java.classgen.handlers;

import javax.xml.stream.events.EndElement;

import ru.csu.stan.java.classgen.automaton.IContext;

/**
 * Обработчик завершающего тега.
 * Закрывает текущее состояние в контексте и возвращается к предыдущему.
 * 
 * @author mz
 *
 */
public class EndElementHandler<T> implements IStaxHandler<T>{

	/** Событие окончания тега*/
	private EndElement event;
	
	/** Конструктор */
	public EndElementHandler(EndElement event){
		this.event = event;
	}
	
	@Override
	public IContext<T> handle(final IContext<T> context) {
		context.finish(event.getName().toString());
		IContext<T> result = context.getPreviousState(event.getName().toString());
		return result;
	}

}
