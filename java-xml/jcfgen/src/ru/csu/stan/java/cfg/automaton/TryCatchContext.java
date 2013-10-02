package ru.csu.stan.java.cfg.automaton;

import java.util.LinkedList;
import java.util.List;

import ru.csu.stan.java.cfg.jaxb.Method;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.jaxb.TryExcept;
import ru.csu.stan.java.cfg.jaxb.TryFinally;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * 
 * @author mz
 *
 */
public class TryCatchContext extends ControlFlowForkContextBase<TryExcept> {
	
	private FlowCursor tryCursor;
	private List<FlowCursor> catchCursors = new LinkedList<FlowCursor>();
	private FlowCursor finallyCursor;

	TryCatchContext(Project resultRoot, ContextBase previousState, FlowCursor cursor, CompilationUnit compilationUnit, Method method) {
		super(resultRoot, previousState, cursor, compilationUnit, method);
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		if ("body".equals(eventName)){
			tryCursor = new FlowCursor();
			return createStandardControlFlowContext(tryCursor);
		}
		if ("catch".equals(eventName)){
			FlowCursor cursor = new FlowCursor();
			catchCursors.add(cursor);
			cursor.setCurrentId(getLastCurrentId());
			cursor.addParentId(getFlowForkBlock().getId().intValue());
			return new ControlFlowContext(getResultRoot(), this, getMethod(), cursor, getCompilationUnit());
		}
		if ("finally".equals(eventName)){
			addCursorDataToCurrent(tryCursor);
			for (FlowCursor cursor: catchCursors)
				addCursorDataToCurrent(cursor);
			TryFinally finallyBlock = getObjectFactory().createTryFinally();
			finallyBlock.setId(getCursor().getCurrentIdBigInteger());
			makeFlowsToCurrent();
			getMethod().getTryExceptOrTryFinallyOrWith().add(finallyBlock);
			getCursor().incrementCurrentId();
			finallyCursor = new FlowCursor();
			finallyCursor.setCurrentId(getCursor().getCurrentId());
			finallyCursor.addParentId(finallyBlock.getId().intValue());
			return new ControlFlowContext(getResultRoot(), this, getMethod(), finallyCursor, getCompilationUnit());
		}
		return this;
	}

	@Override
	public void finish(String eventName) {
		if (isEventFitToContext(eventName)){
			if (finallyCursor == null){
				addCursorDataToCurrent(tryCursor);
				for (FlowCursor cursor: catchCursors)
					addCursorDataToCurrent(cursor);
			}
			else{
				getCursor().clearParentIds();
				addCursorDataToCurrent(finallyCursor);
			}
		}
	}

	@Override
	protected TryExcept createFlowForkBlock() {
		return getObjectFactory().createTryExcept();
	}

	@Override
	protected String[] getTagNames() {
		return new String[] {"try"};
	}

	private int getLastCurrentId(){
		int last = tryCursor.getCurrentId();
		for (FlowCursor cursor: catchCursors)
			if (cursor.getCurrentId() > last)
				last = cursor.getCurrentId();
		return last;
	}
	
}
