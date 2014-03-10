package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.automaton.base.ContextBase;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.util.MethodRegistryItem;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;

/**
 * 
 * @author mz
 *
 */
public class ArgContext extends ContextBase {

	private MethodRegistryItem registry;
	
	ArgContext(ContextBase previousState, MethodRegistryItem registryItem) {
		super(previousState);
		this.registry = registryItem;
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
		return this;
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {
		if ("variable".equals(name)){
			this.registry.addArg(attrs.getNameAttribute());
		}
	}

	@Override
	public void finish(String eventName) {

	}

}
