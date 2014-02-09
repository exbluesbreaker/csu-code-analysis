package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.For;
import ru.csu.stan.java.cfg.jaxb.Method;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * 
 * @author mz
 *
 */
public class ForContext extends ControlFlowForkContextBase<For> {

	private FlowCursor bodyCursor;
	
	ForContext(Project resultRoot, ContextBase previousState, FlowCursor cursor, CompilationUnit compilationUnit, Method method) {
		super(resultRoot, previousState, cursor, compilationUnit, method);
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		if ("body".equals(eventName)){
			bodyCursor = new FlowCursor();
			return createStandardControlFlowContext(bodyCursor);
		}
		return this;
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {
		super.processTag(name, attrs);
		if ("initialize_section".equals(name))
			if (getFlowForkBlock() != null)
				getFlowForkBlock().setIterate("initialize_section");
		if ("expression".equals(name))
			if (getFlowForkBlock() != null)
				getFlowForkBlock().setIterate("expression");
	}

	@Override
	public void finish(String eventName) {
		if (isEventFitToContext(eventName)){
			makeFlowsFromCursorToId(bodyCursor, getFlowForkBlock().getId());
			getCursor().setCurrentId(bodyCursor.getCurrentId());
			getCursor().addParentId(getFlowForkBlock().getId().intValue());
		}
	}

	@Override
	protected For createFlowForkBlock() {
		return getObjectFactory().createFor();
	}

	@Override
	protected String[] getTagNames() {
		return new String[] {"for_loop", "enhanced_for_loop"};
	}

}
