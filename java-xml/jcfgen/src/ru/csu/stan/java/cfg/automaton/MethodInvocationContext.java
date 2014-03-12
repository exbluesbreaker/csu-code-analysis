package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;

import ru.csu.stan.java.cfg.automaton.base.ContextBase;
import ru.csu.stan.java.cfg.jaxb.Block;
import ru.csu.stan.java.cfg.jaxb.Call;
import ru.csu.stan.java.cfg.jaxb.Direct;
import ru.csu.stan.java.cfg.jaxb.Getattr;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.jaxb.Target;
import ru.csu.stan.java.cfg.jaxb.TargetClass;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;

/**
 * 
 * @author mz
 *
 */
public class MethodInvocationContext extends ContextBase {

	private Block block;
	private String name;
	private String label;
	private Call call;
	private boolean hasInternalCall;
	private String className;
	
	MethodInvocationContext(ContextBase previousState, Block block, String className) {
		super(previousState);
		this.block = block;
		this.className = className;
	}

	@Override
	public IContext<Project> getPreviousState(String eventName) {
		if ("method_invocation".equals(eventName))
			return getUpperState();
		else
			return this;
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		if ("method_invocation".equals(eventName)){
			hasInternalCall = true;
        	return new MethodInvocationContext(this, block, className);
        }
		if ("arguments".equals(eventName))
			return new MethodArgumentsContext(this);
		return this;
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {
		if ("method_invocation".equals(name)){
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
			label = attrs.getNameAttribute();
		}
	}

	@Override
	public void finish(String eventName) {
		if ("method_invocation".equals(eventName)){
			if (!hasInternalCall){
				if (name == null || name.isEmpty()){
					Direct direct = getObjectFactory().createDirect();
					direct.setName(label);
					Target target = getObjectFactory().createTarget();
					target.setType("method");
					TargetClass tc = getObjectFactory().createTargetClass();
					tc.setLabel(className);
					direct.setTarget(target);
					call.setDirect(direct);
				}
				else{
					Getattr getattr = getObjectFactory().createGetattr();
					getattr.setName(name);
					getattr.setLabel(label);
					call.setGetattr(getattr);
				}
				block.getCall().add(call);
			}
		}
	}

}
