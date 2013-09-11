package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;
import java.util.LinkedList;

import ru.csu.stan.java.cfg.jaxb.Block;
import ru.csu.stan.java.cfg.jaxb.Flow;
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
class ControlFlowContext extends ContextBase{
	
	private Method method;
    private final FlowCursor cursor;
    private CompilationUnit compilationUnit;
    private Block block;
    private String startTag = "";

    ControlFlowContext(Project resultRoot, ContextBase previousState, Method method, final FlowCursor cursor, CompilationUnit compilationUnit){
        super(resultRoot, previousState);
        this.method = method;
        this.cursor = cursor;
        this.compilationUnit = compilationUnit;
    }

    @Override
    public IContext<Project> getPreviousState(String eventName){   
        if ("block".equals(eventName))
            return getPreviousState();
        if (startTag.equals(eventName))
        	return getPreviousState();
        return this;
    }

    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName){
        if ("class".equals(eventName))
            return new ClassContext(getResultRoot(), this, compilationUnit);
        if ("if".equals(eventName)){
            block = null;
            return new IfContext(getResultRoot(), this, cursor, compilationUnit, method);
        }
        if ("while_loop".equals(eventName) || "do_while_loop".equals(eventName)){
        	block = null;
        	return new WhileContext(getResultRoot(), this, cursor, compilationUnit, method);
        }
        if ("for_loop".equals(eventName) || "enhanced_for_loop".equals(eventName)){
        	block = null;
        	return new ForContext(getResultRoot(), this, cursor, compilationUnit, method);
        }
        if ("try".equals(eventName)){
        	block = null;
        	return new TryCatchContext(getResultRoot(), this, cursor, compilationUnit, method);
        }
        return this;
    }

    @Override
    public void processTag(String name, NodeAttributes attrs){
    	if ("body".equals(name))
    		return;
    	if (startTag == null || "".equals(startTag))
    		startTag = name;
        if (block == null && isNotOpeningTag(name)){
        	makeFlowsToCurrent();
            block = getObjectFactory().createBlock();
            block.setId(BigInteger.valueOf(cursor.getCurrentId()));
            if (attrs.isAttributeExist(NodeAttributes.LINE_ATTRIBUTE))
            	block.setFromlineno(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.LINE_ATTRIBUTE)));
            if (attrs.isAttributeExist(NodeAttributes.COL_ATTRIBUTE))
            	block.setColOffset(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.COL_ATTRIBUTE)));
            method.getTryExceptOrTryFinallyOrWith().add(block);
            cursor.setParentIds(new LinkedList<Integer>());
            cursor.addParentId(cursor.getCurrentId());
            cursor.incrementCurrentId();
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

    @Override
    public void finish(String eventName){

    }

    private boolean isNotOpeningTag(String tag){
    	return !("block".equals(tag) || "body".equals(tag) || "nodename.statements".equals(tag) || "then_part".equals(tag) || "else_part".equals(tag) || "finally".equals(tag) || "catch".equals(tag));
    }
}
