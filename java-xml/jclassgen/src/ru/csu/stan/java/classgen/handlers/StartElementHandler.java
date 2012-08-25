package ru.csu.stan.java.classgen.handlers;

import java.util.Iterator;

import javax.xml.stream.events.Attribute;
import javax.xml.stream.events.StartElement;

import ru.csu.stan.java.classgen.util.ClassContext;

public class StartElementHandler implements IStaxHandler {

	private StartElement event;
	
	public StartElementHandler(StartElement event){
		this.event = event;
	}
	
	@Override
	public ClassContext handle(final ClassContext context) {
		if (event.getName().toString().equals("package")){
			context.setPackageState();
		}
		if (event.getName().toString().equals("class")){
			context.setClassState();
		}
		if (event.getName().toString().equals("method")){
			context.setMethodState();
		}
		if (event.getName().toString().equals("variable")){
			context.setStateForVar();
		}
		if (event.getName().toString().equals("extends") || 
				event.getName().toString().equals("implements")){
			context.setParentState();
		}
		if (event.getName().toString().equals("import")){
			context.setImportState();
		}
		if (event.getName().toString().equals("block")){
			context.setEmptyState();
		}
		if (event.getName().toString().equals("new_class")){
			context.setNewClassState();
		}
		if (event.getName().toString().equals("arguments")){
			context.setEmptyState();
		}
		@SuppressWarnings("unchecked")
		Iterator<Attribute> it =event.getAttributes();
		context.processTag(event.getName().toString(), it);
		return context;
	}

}
