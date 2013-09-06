package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Method;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.jaxb.TryExcept;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * 
 * @author mz
 *
 */
public class TryCatchContext extends ControlFlowForkContextBase<TryExcept> {

	TryCatchContext(Project resultRoot, ContextBase previousState, FlowCursor cursor, CompilationUnit compilationUnit, Method method) {
		super(resultRoot, previousState, cursor, compilationUnit, method);
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		return this;
	}

	@Override
	public void finish(String eventName) {

	}

	@Override
	protected TryExcept createFlowForkBlock() {
		return getObjectFactory().createTryExcept();
	}

	@Override
	protected String[] getTagNames() {
		return new String[] {"try"};
	}

}
