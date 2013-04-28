package ru.csu.stan.java.classgen.handlers;

import javax.xml.stream.events.EndElement;

import ru.csu.stan.java.classgen.util.ClassContext;

/**
 * Обработчик завершающего тега.
 * Закрывает текущее состояние в контексте и возвращается к предыдущему.
 * 
 * @author mz
 *
 */
public class EndElementHandler implements IStaxHandler{

	/** Событие окончания тега*/
	private EndElement event;
	
	/** Конструктор */
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
			event.getName().toString().equals("modifiers") ||
			event.getName().toString().equals("compilation_unit") ){
			context.finish();
			context.setPreviousState();
		}
		
		if (event.getName().toString().equals("variable"))
		{
			context.finishVar();
			context.setPreviousVarState();
		}
		
		if (event.getName().toString().equals("identifier"))
			context.finishIdentifier();
		
		if (event.getName().toString().equals("vartype"))
		{
			context.finishVartype();
			context.setPreviousVartypeState();
		}
		
		return context;
	}

}
