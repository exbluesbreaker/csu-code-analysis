package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.automaton.base.ContextBase;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.util.scope.VariableFromScope;
import ru.csu.stan.java.cfg.util.scope.VariableScope;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;

/**
 * 
 * @author mz
 *
 */
public class VariableContext extends ContextBase {

	private VariableScope scope;
	private VariableFromScope scopedVar;
	
	VariableContext(ContextBase previousState, VariableScope scope) {
		super(previousState);
		this.scope = scope;
		scopedVar = new VariableFromScope();
	}

	@Override
	public IContext<Project> getPreviousState(String eventName) {
		if ("variable".equals(eventName))
			return getUpperState();
		else
			return this;
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		if ("vartype".equals(eventName))
			return new VartypeContext(this, scopedVar);
		return this;
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {
		if ("variable".equals(name))
			scopedVar.setName(attrs.getNameAttribute());
	}

	@Override
	public void finish(String eventName) {
		if ("variable".equals(eventName)){
			this.scope.addVar(scopedVar);
		}
	}

}
