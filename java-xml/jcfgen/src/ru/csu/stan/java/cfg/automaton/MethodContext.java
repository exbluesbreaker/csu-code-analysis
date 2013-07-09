package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;
import java.util.Iterator;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.cfg.jaxb.Method;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
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
    private int id;
    private String className;
    private String name;
    private CompilationUnit compilationUnit;

    MethodContext(Project resultRoot, ContextBase previousState, String className, int id, CompilationUnit compilationUnit)
    {
        super(resultRoot, previousState);
        this.className = className;
        this.id = id;
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
        return this;
    }

    @Override
    public void processTag(String name, Iterator<Attribute> attrs)
    {
    	if ("method".equals(name))
		{
			String nameAttr = getNameAttr(attrs);
			if ("<init>".equals(nameAttr))
				nameAttr = className.substring(className.lastIndexOf('.')+1);
			name = nameAttr;
		}
    }

    @Override
    public void finish(String eventName)
    {
        if ("method".equals(eventName))
        {
            Method method = getObjectFactory().createMethod();
            method.setParentClass(className);
            method.setId(BigInteger.valueOf(id));
            method.setName(name);
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
