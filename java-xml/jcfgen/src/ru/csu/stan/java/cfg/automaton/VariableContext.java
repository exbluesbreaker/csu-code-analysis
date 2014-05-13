package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.automaton.base.ContextBase;
import ru.csu.stan.java.cfg.automaton.base.IClassInsidePart;
import ru.csu.stan.java.cfg.jaxb.Block;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.util.scope.VariableFromScope;
import ru.csu.stan.java.cfg.util.scope.VariableScope;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * 
 * @author mz
 *
 */
public class VariableContext extends ContextBase implements IClassInsidePart{

	private VariableScope scope;
	private VariableFromScope scopedVar;
	private Block block;
	private CompilationUnit compilationUnit;
	
	VariableContext(ContextBase previousState, VariableScope scope, Block block, CompilationUnit compilationUnit) {
		super(previousState);
		this.scope = scope;
		scopedVar = new VariableFromScope();
		this.block = block;
		this.compilationUnit = compilationUnit;
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
		if (block != null){
			if ("method_invocation".equals(eventName)){
	        	return new MethodInvocationContext(this, block, getClassName(), compilationUnit);
	        }
	        if ("new_class".equals(eventName)){
	        	return new NewClassContext(this, block, getClassName(), compilationUnit);
	        }
		}
		if ("class".equals(eventName)){
			return new ClassContext(this, compilationUnit);
		}
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
	
	@Override
	public String getClassName() {
		return findParentClassNameHolder().getClassName();
	}

	@Override
	public int getNextInnerCount() {
		return findParentClassNameHolder().getNextInnerCount();
	}
	
	private IClassInsidePart findParentClassNameHolder(){
		ContextBase ctx = this.getUpperState();
		while (!(ctx instanceof IClassInsidePart) && ctx != null)
			ctx = ctx.getUpperState();
		return (IClassInsidePart) ctx;
	}

	@Override
	public VariableScope getVariableScope() {
		return findParentClassNameHolder().getVariableScope();
	}

}
