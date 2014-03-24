package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.automaton.base.ContextBase;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.util.scope.VariableFromScope;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;

/**
 * 
 * @author mz
 *
 */
public class VartypeContext extends ContextBase {

	private VariableFromScope var;
	private String typeName = "";
	boolean parameterized = false;
	boolean arguments = false;
	
	protected VartypeContext(ContextBase previousState, VariableFromScope scopedVar) {
		super(previousState);
		this.var = scopedVar;
	}

	@Override
	public IContext<Project> getPreviousState(String eventName) {
		if ("vartype".equals(eventName))
			return getUpperState();
		else
			return this;
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		return this;
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {
		if ("parameterized_type".equals(name))
			parameterized = true;
		if ("arguments".equals(name))
			arguments = true;
		if (!arguments){
			if ("identifier".equals(name) || "member_select".equals(name) || "primitive_type".equals(name))
				if (typeName.isEmpty())
					typeName = attrs.getNameAttribute();
				else
					typeName = attrs.getNameAttribute() + "." + typeName;
				
		}
	}

	@Override
	public void finish(String eventName) {
		if ("vartype".equals(eventName))
			var.setType(typeName);
	}

}
