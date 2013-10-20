package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;

import ru.csu.stan.java.cfg.jaxb.Block;
import ru.csu.stan.java.cfg.jaxb.Flow;
import ru.csu.stan.java.cfg.jaxb.Method;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * Состояние анализа метода.
 * Создает методы - основные единицы CFG и добавляет их в результат.
 * 
 * @author mzubov
 *
 */
class MethodContext extends ContextBase implements IClassNameHolder
{
    private String className;
    private String name;
    private CompilationUnit compilationUnit;
    private Method method;
    private FlowCursor innerCursor = new FlowCursor();

    MethodContext(Project resultRoot, ContextBase previousState, String className, CompilationUnit compilationUnit)
    {
        super(resultRoot, previousState);
        this.className = className;
        this.compilationUnit = compilationUnit;
    }

    @Override
    public IContext<Project> getPreviousState(String eventName)
    {
        if ("method".equals(eventName))
            return getPreviousState();
        return this;
    }

    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName)
    {
    	if ("class".equals(eventName))
            return new ClassContext(getResultRoot(), this, compilationUnit);
    	if ("block".equals(eventName))
    	    return new ControlFlowContext(getResultRoot(), this, method, innerCursor, compilationUnit);
        return this;
    }

    @Override
    public void processTag(String name, NodeAttributes attrs)
    {
    	if ("method".equals(name))
		{
			String nameAttr = attrs.getNameAttribute();
			if ("<init>".equals(nameAttr))
				nameAttr = className.substring(className.lastIndexOf('.')+1);
			this.name = nameAttr;
			method = getObjectFactory().createMethod();
            method.setParentClass(className);
            method.setName(this.name);
		}
    }

    @Override
    public void finish(String eventName)
    {
        if ("method".equals(eventName)){
        	for (Integer parent: innerCursor.getParentIds()){
        		int flowParent = parent.intValue() > 0 ? parent.intValue() : (-1) * parent.intValue();
        		Flow flow = getObjectFactory().createFlow();
        		flow.setFromId(BigInteger.valueOf(flowParent));
        		flow.setToId(innerCursor.getCurrentIdBigInteger());
        		method.getTryExceptOrTryFinallyOrWith().add(flow);
        	}
        	Block exitBlock = getObjectFactory().createBlock();
        	exitBlock.setType("<<Exit>>");
        	exitBlock.setId(innerCursor.getCurrentIdBigInteger());
        	method.getTryExceptOrTryFinallyOrWith().add(exitBlock);
            getResultRoot().getMethodOrFunction().add(method);
        }
    }

	@Override
	public String getClassName() {
		return className;
	}

	@Override
	public int getNextInnerCount() {
		if (getPreviousState() instanceof IClassNameHolder)
			return ((IClassNameHolder)getPreviousState()).getNextInnerCount();
		else
			return 0;
	}

}
