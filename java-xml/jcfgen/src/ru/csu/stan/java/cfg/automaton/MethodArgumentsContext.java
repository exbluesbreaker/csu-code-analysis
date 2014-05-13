package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.automaton.base.ContextBase;
import ru.csu.stan.java.cfg.automaton.base.IClassInsidePart;
import ru.csu.stan.java.cfg.jaxb.Block;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.util.scope.VariableScope;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * 
 * @author mz
 *
 */
public class MethodArgumentsContext extends ContextBase implements IClassInsidePart {

	private Block block;
	private String className;
	private CompilationUnit compilationUnit;
	
	protected MethodArgumentsContext(ContextBase previousState, Block block, String className, CompilationUnit compilationUnit) {
		super(previousState);
		this.block = block;
		this.className = className;
		this.compilationUnit = compilationUnit;
	}

	@Override
	public IContext<Project> getPreviousState(String eventName) {
		if ("arguments".equals(eventName))
			return getUpperState();
		return this;
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		if ("new_class".equals(eventName)){
			setInternalCall();
        	return new NewClassContext(this, block, className, compilationUnit);
        }
		if ("method_invocation".equals(eventName)){
			setInternalCall();
        	return new MethodInvocationContext(this, block, className, compilationUnit);
        }
		return this;
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {
		
	}

	@Override
	public void finish(String eventName) {

	}
	
	public void setInternalCall() {
		if (getUpperState() instanceof MethodInvocationContext)
			((MethodInvocationContext)getUpperState()).setInternalCall();
		if (getUpperState() instanceof MethodArgumentsContext)
			((MethodArgumentsContext)getUpperState()).setInternalCall();
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
