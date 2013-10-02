package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;

import ru.csu.stan.java.cfg.jaxb.BaseCfgElement;
import ru.csu.stan.java.cfg.jaxb.Flow;
import ru.csu.stan.java.cfg.jaxb.Method;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * Реализация базово-условного блока, который делает разветвление в графе потока управления.
 * Это могут быть условия, циклы итп.
 * 
 * @author mz
 *
 * @param <T> конкретный тип блока
 */
abstract class ControlFlowForkContextBase<T extends BaseCfgElement> extends ContextBase {
	
	private FlowCursor cursor;
    private T flowForkBlock;
    private CompilationUnit compilationUnit;
    private Method method;

	ControlFlowForkContextBase(Project resultRoot, ContextBase previousState, FlowCursor cursor, CompilationUnit compilationUnit, Method method) {
		super(resultRoot, previousState);
		this.cursor = cursor;
		this.compilationUnit = compilationUnit;
		this.method = method;
	}

	@Override
	public IContext<Project> getPreviousState(String eventName) {
		for (String tag: getTagNames())
			if (tag.equals(eventName))
				return getPreviousState();
		return this;
	}

	@Override
	public void processTag(String name, NodeAttributes attrs) {
		if (isEventFitToContext(name)){
			makeFlowsToCurrent();
			flowForkBlock = createFlowForkBlock();
			flowForkBlock.setFromlineno(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.LINE_ATTRIBUTE)));
			flowForkBlock.setColOffset(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.COL_ATTRIBUTE)));
			flowForkBlock.setId(cursor.getCurrentIdBigInteger());
            cursor.incrementCurrentId();
            method.getTryExceptOrTryFinallyOrWith().add(flowForkBlock);
		}
	}
	
	protected abstract T createFlowForkBlock();
	
	protected boolean isEventFitToContext(String eventName){
		for (String tag: getTagNames())
			if (tag.equals(eventName))
				return true;
		return false;
	}
	
	protected abstract String[] getTagNames();

	protected void makeFlowsToCurrent(){
    	for (Integer parent: cursor.getParentIds()){
    		if (parent.intValue() > 0){
	    		Flow flow = getObjectFactory().createFlow();
	    		flow.setFromId(BigInteger.valueOf(parent.longValue()));
	    		flow.setToId(cursor.getCurrentIdBigInteger());
	    		method.getTryExceptOrTryFinallyOrWith().add(flow);
    		}
    	}
    }
	
	protected T getFlowForkBlock(){
		return flowForkBlock;
	}
	
	protected FlowCursor getCursor(){
		return cursor;
	}
	
	protected Method getMethod(){
		return method;
	}
	
	protected CompilationUnit getCompilationUnit(){
		return compilationUnit;
	}
	
	protected void addCursorDataToCurrent(FlowCursor additionCursor){
		if (additionCursor != null){
			for (Integer i: additionCursor.getParentIds())
				cursor.addParentId(i.intValue());
			cursor.setCurrentId(additionCursor.getCurrentId());
		}
	}
	
	protected IContext<Project> createStandardControlFlowContext(final FlowCursor innerCursor){
		cursor.clearParentIds();
		innerCursor.setCurrentId(cursor.getCurrentId());
		innerCursor.clearParentIds();
		innerCursor.addParentId(flowForkBlock.getId().intValue());
        return new ControlFlowContext(getResultRoot(), this, method, innerCursor, compilationUnit);
	}
}
