package ru.csu.stan.java.classgen.handlers;

import javax.xml.stream.events.XMLEvent;

/**
 * Фабрика обработчиков STAX-событий.
 * В зависимости от типа события создает необходимый обработчик.
 * 
 * @author mz
 *
 */
public class HandlerFactory {

	/** \
	 * Закрытый конструктор по-умолчанию.
	 * @see #getInstance() 
	 */
	private HandlerFactory(){}
	
	/**
	 * Статический метод генерации для получения экземпляра фабрики.
	 * @return
	 */
	public static HandlerFactory getInstance(){
		return new HandlerFactory();
	}
	
	/**
	 * Создание обработчика STAX-события по самому событию.
	 * @param xmlEvent
	 * @return
	 */
	public IStaxHandler createHandler(XMLEvent xmlEvent){
		switch (xmlEvent.getEventType()){
			case XMLEvent.ATTRIBUTE:
				return new NothingToDoHandler();
			case XMLEvent.CHARACTERS:
				return new NothingToDoHandler();
			case XMLEvent.END_DOCUMENT:
				return new NothingToDoHandler();
			case XMLEvent.END_ELEMENT:
				return new EndElementHandler(xmlEvent.asEndElement());
			case XMLEvent.START_DOCUMENT:
				return new NothingToDoHandler();
			case XMLEvent.START_ELEMENT:
				return new StartElementHandler(xmlEvent.asStartElement());
			default:
				return new NothingToDoHandler();
		}
	}
}
