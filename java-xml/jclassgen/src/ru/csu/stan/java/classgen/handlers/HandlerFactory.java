package ru.csu.stan.java.classgen.handlers;

import javax.xml.stream.events.XMLEvent;

public class HandlerFactory {

	private HandlerFactory(){}
	
	public static HandlerFactory getInstance(){
		return new HandlerFactory();
	}
	
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
