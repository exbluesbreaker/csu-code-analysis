package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;

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
class IfContext extends ContextBase
{
    private FlowCursor cursor;
    private FlowCursor thenCursor;
    private FlowCursor elseCursor;
    private If ifBlock;
    private CompilationUnit compilationUnit;
    private Method method;

    IfContext(Project resultRoot, ContextBase previousState, FlowCursor cursor, CompilationUnit compilationUnit, Method method)
    {
        super(resultRoot, previousState);
        this.cursor = cursor;
        this.compilationUnit = compilationUnit;
        this.method = method;
    }

    @Override
    public IContext<Project> getPreviousState(String eventName)
    {
        if ("if".equals(eventName))
            return getPreviousState();
        return this;
    }

    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName)
    {
        if ("then_part".equals(eventName)){
            thenCursor = cursor.clone();
            return new ControlFlowContext(getResultRoot(), this, method, thenCursor, compilationUnit);
        }
        if ("else_part".equals(eventName)){
            elseCursor = cursor.clone();
            if (thenCursor != null)
                elseCursor.setCurrentId(thenCursor.getCurrentId());
            return new ControlFlowContext(getResultRoot(), this, method, elseCursor, compilationUnit);
        }
        return this;
    }

    @Override
    public void processTag(String name, NodeAttributes attrs)
    {
        if ("condition".equals(name)){
            if (ifBlock != null)
                ifBlock.setTest("condition");
        }
        if ("if".equals(name)){
            If ifBlock = getObjectFactory().createIf();
            ifBlock.setFromlineno(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.LINE_ATTRIBUTE)));
            ifBlock.setColOffset(BigInteger.valueOf(attrs.getIntAttribute(NodeAttributes.COL_ATTRIBUTE)));
            ifBlock.setId(cursor.getCurrentIdBigInteger());
            cursor.incrementCurrentId();
            method.getTryExceptOrTryFinallyOrWith().add(ifBlock);
        }
    }

    @Override
    public void finish(String eventName)
    {
        if ("if".equals(eventName)){
            if (thenCursor != null){
                for (Integer i: thenCursor.getParentIds())
                    cursor.addParentId(i.intValue());
                cursor.setCurrentId(thenCursor.getCurrentId());
            }
            if (elseCursor != null){
                for (Integer i: elseCursor.getParentIds())
                    cursor.addParentId(i.intValue());
                cursor.setCurrentId(elseCursor.getCurrentId());
            }
        }
    }

}
