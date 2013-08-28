package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;

import ru.csu.stan.java.cfg.jaxb.Flow;
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
class WhileContext extends ContextBase {

	private FlowCursor cursor;
    private FlowCursor bodyCursor;
    private While whileBlock;
    private CompilationUnit compilationUnit;
    private Method method;
	
	WhileContext(Project resultRoot, ContextBase previousState, FlowCursor cursor, CompilationUnit compilationUnit, Method method) {
		super(resultRoot, previousState);
		this.cursor = cursor;
		this.compilationUnit = compilationUnit;
		this.method = method;
	}

	@Override
	public IContext<Project> getPreviousState(String eventName) {
		if ("while_loop".equals(eventName) || "do_while_loop".equals(eventName))
			return getPreviousState();
		else
			return this;
	}

	@Override
	public IContext<Project> getNextState(IContext<Project> context, String eventName) {
		if ("body".equals(eventName)){
			cursor.clearParentIds();
			bodyCursor = cursor.clone();
			bodyCursor.addParentId(whileBlock.getId().intValue());
            return new ControlFlowContext(getResultRoot(), this, method, bodyCursor, compilationUnit);
		}
		return this;
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {
		if ("condition".equals(name)){
			if (whileBlock != null)
				whileBlock.setTest("condition");
		}
		if ("while_loop".equals(name) || "do_while_loop".equals(name)){
			makeFlowsToCurrent();
			whileBlock = getObjectFactory().createWhile();
			whileBlock.setFromlineno(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.LINE_ATTRIBUTE)));
			whileBlock.setColOffset(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.COL_ATTRIBUTE)));
			whileBlock.setId(cursor.getCurrentIdBigInteger());
            cursor.incrementCurrentId();
            method.getTryExceptOrTryFinallyOrWith().add(whileBlock);
		}
	}

	@Override
	public void finish(String eventName) {
		if ("while_loop".equals(eventName) || "do_while_loop".equals(eventName)){
			if (bodyCursor != null){
				for (Integer i: bodyCursor.getParentIds())
					cursor.addParentId(i.intValue());
				cursor.setCurrentId(bodyCursor.getCurrentId());
			}
		}
	}

	private void makeFlowsToCurrent(){
    	for (Integer parent: cursor.getParentIds()){
    		Flow flow = getObjectFactory().createFlow();
    		flow.setFromId(BigInteger.valueOf(parent.longValue()));
    		flow.setToId(cursor.getCurrentIdBigInteger());
    		method.getTryExceptOrTryFinallyOrWith().add(flow);
    	}
    }
}
