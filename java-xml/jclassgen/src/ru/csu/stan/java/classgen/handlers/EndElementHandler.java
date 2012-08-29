package ru.csu.stan.java.classgen.handlers;

import javax.xml.stream.events.EndElement;

import ru.csu.stan.java.classgen.util.ClassContext;

public class EndElementHandler implements IStaxHandler{

	private EndElement event;
	
	public EndElementHandler(EndElement event){
		this.event = event;
	}
	
	@Override
	public ClassContext handle(final ClassContext context) {
		if (event.getName().toString().equals("package") ||
			event.getName().toString().equals("class") ||
			event.getName().toString().equals("method") ||
			event.getName().toString().equals("extends") || 
			event.getName().toString().equals("implements") ||
			event.getName().toString().equals("import") ||
			event.getName().toString().equals("block") ||
			event.getName().toString().equals("new_class") ||
			event.getName().toString().equals("arguments") || 
			event.getName().toString().equals("compilation_unit") ){
			context.finish();
			context.setPreviousState();
		}
		if (event.getName().toString().equals("variable"))
		{
			context.finishVar();
			context.setPreviousVarState();
		}
		return context;
	}

}
