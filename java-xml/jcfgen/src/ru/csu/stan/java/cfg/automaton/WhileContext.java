package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Method;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.jaxb.While;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * 
 * @author mz
 *
 */
class WhileContext extends ControlFlowForkContextBase<While> {

    private FlowCursor bodyCursor;
	
	WhileContext(ContextBase previousState, FlowCursor cursor, CompilationUnit compilationUnit, Method method) {
		super(previousState, cursor, compilationUnit, method);
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
		if ("condition".equals(name)){
			if (getFlowForkBlock() != null)
				getFlowForkBlock().setTest("condition");
		}
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
	protected While createFlowForkBlock() {
		return getObjectFactory().createWhile();
	}

	@Override
	protected String[] getTagNames() {
		return new String[] {"while_loop", "do_while_loop"};
	}
}
