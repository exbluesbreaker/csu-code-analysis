package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;
import java.util.Iterator;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.cfg.jaxb.Method;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;

/**
 * Состояние анализа метода.
 * Создает методы - основные единицы CFG и добавляет их в результат.
 * 
 * @author mzubov
 *
 */
public class MethodContext extends ContextBase
{
    private int id;
    private String className;
    private String name;

    MethodContext(Project resultRoot, ContextBase previousState, String className, int id)
    {
        super(resultRoot, previousState);
        this.className = className;
        this.id = id;
    }

    @Override
    public IContext<Project> getPreviousState(String eventName)
    {
        if ("method".equals(eventName))
            return getPreviousState();
        else
            return this;
    }

    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName)
    {
        return this;
    }

    @Override
    public void processTag(String name, Iterator<Attribute> attrs)
    {

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
        }
    }

}
