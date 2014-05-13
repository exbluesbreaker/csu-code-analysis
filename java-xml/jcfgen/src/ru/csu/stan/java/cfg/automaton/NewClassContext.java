package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;

import ru.csu.stan.java.cfg.automaton.base.ContextBase;
import ru.csu.stan.java.cfg.automaton.base.IClassInsidePart;
import ru.csu.stan.java.cfg.jaxb.Block;
import ru.csu.stan.java.cfg.jaxb.Call;
import ru.csu.stan.java.cfg.jaxb.Direct;
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
public class NewClassContext extends ContextBase implements IClassInsidePart{
	
	private Block block;
	private String name;
	private Call call;
	private String className;
	private CompilationUnit compilationUnit;
	
	protected NewClassContext(ContextBase previousState, Block block, String className, CompilationUnit compilationUnit) {
		super(previousState);
		this.block = block;
		this.className = className;
		this.compilationUnit = compilationUnit;
	}

	@Override
	public IContext<Project> getPreviousState(String eventName) {
		if ("new_class".equals(eventName))
			return getUpperState();
		return this;
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		if ("method_invocation".equals(eventName)){
        	return new MethodInvocationContext(this, block, className, compilationUnit);
        }
		if ("new_class".equals(eventName)){
        	return new NewClassContext(this, block, className, compilationUnit);
        }
		if ("class".equals(eventName)){
			return new ClassContext(this, compilationUnit);
		}
		return this;
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {
		if ("new_class".equals(name)){
			call = getObjectFactory().createCall();
			if (attrs.isAttributeExist(NodeAttributes.LINE_ATTRIBUTE))
				call.setFromlineno(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.LINE_ATTRIBUTE)));
            if (attrs.isAttributeExist(NodeAttributes.COL_ATTRIBUTE))
            	call.setColOffset(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.COL_ATTRIBUTE)));
		}
		if ("member_select".equals(name)){
			if (this.name == null || this.name.isEmpty())
				this.name = attrs.getNameAttribute();
			else
				this.name = attrs.getNameAttribute() + '.' + this.name;
		}
		if ("identifier".equals(name)){
			if (this.name == null || this.name.isEmpty())
				this.name = attrs.getNameAttribute();
			else
				this.name = attrs.getNameAttribute() + '.' + this.name;
		}
	}

	@Override
	public void finish(String eventName) {
		if ("new_class".equals(eventName)){
			if (name != null && !name.isEmpty()){
				Direct direct = getObjectFactory().createDirect();
				direct.setName(name);
				call.setDirect(direct);
			}
			block.getCall().add(call);
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
