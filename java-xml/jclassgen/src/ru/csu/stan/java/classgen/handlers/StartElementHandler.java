package ru.csu.stan.java.classgen.handlers;

import java.util.Iterator;

import javax.xml.stream.events.Attribute;
import javax.xml.stream.events.StartElement;

import ru.csu.stan.java.classgen.automaton.IContext;

/**
 * Обработчик события начала тега.
 * Использует контекст классов (автомат).
 * Переводит его в новое состояние при получении соответствующего тега.
 * 
 * @author mz
 *
 */
public class StartElementHandler<T> implements IStaxHandler<T> {

	private StartElement event;
	
	public StartElementHandler(StartElement event){
		this.event = event;
	}
	
	@Override
	public IContext<T> handle(final IContext<T> context) {
		IContext<T> result = context.getNextState(context, event.getName().toString());
		@SuppressWarnings("unchecked")
		Iterator<Attribute> it = event.getAttributes();
		result.processTag(event.getName().toString(), it);
		return result;
	}

}
