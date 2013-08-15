package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;
import java.util.Arrays;

import ru.csu.stan.java.cfg.jaxb.Block;
import ru.csu.stan.java.cfg.jaxb.If;
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
class ControlFlowContext extends ContextBase
{
    private Method method;
    private FlowCursor cursor;
    private CompilationUnit compilationUnit;
    private Block block;

    ControlFlowContext(Project resultRoot, ContextBase previousState, Method method, FlowCursor cursor, CompilationUnit compilationUnit)
    {
        super(resultRoot, previousState);
        this.method = method;
        this.cursor = cursor;
        this.compilationUnit = compilationUnit;
    }

    @Override
    public IContext<Project> getPreviousState(String eventName)
    {   
        if ("block".equals(eventName))
            return getPreviousState();
        return this;
    }

    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName)
    {
        if ("class".equals(eventName))
            return new ClassContext(getResultRoot(), this, compilationUnit);
        return this;
    }

    @Override
    public void processTag(String name, NodeAttributes attrs)
    {
        if ("if".equals(name)){
            If ifBlock = getObjectFactory().createIf();
            ifBlock.setFromlineno(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.LINE_ATTRIBUTE)));
            ifBlock.setColOffset(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.COL_ATTRIBUTE)));
            method.getTryExceptOrTryFinallyOrWith().add(ifBlock);
            // TODO: а здесь разбираем его внутренности
            block = null;
            return;
        }
        if (block == null){
            block = getObjectFactory().createBlock();
            block.setId(BigInteger.valueOf(cursor.getCurrentId()));
            block.setFromlineno(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.LINE_ATTRIBUTE)));
            block.setColOffset(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.COL_ATTRIBUTE)));
            method.getTryExceptOrTryFinallyOrWith().add(block);
            cursor.setParentIds(Arrays.asList(Integer.valueOf(cursor.getCurrentId())));
            cursor.incrementCurrentId();
        }
    }

    @Override
    public void finish(String eventName)
    {

    }

}
