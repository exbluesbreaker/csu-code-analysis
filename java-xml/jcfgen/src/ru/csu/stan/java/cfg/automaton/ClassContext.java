package ru.csu.stan.java.cfg.automaton;

import java.util.Iterator;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * Состояние анализа класса.
 * 
 * @author mzubov
 *
 */
class ClassContext extends ContextBase
{
    private String name = "";
    private int methodId = 1;
    private int innerCount;
    private CompilationUnit compilationUnit;

    ClassContext(Project resultRoot, ContextBase previousState, CompilationUnit compilationUnit)
    {
        super(resultRoot, previousState);
        this.compilationUnit = compilationUnit;
    }

    @Override
    public IContext<Project> getPreviousState(String eventName)
    {
        if ("class".equals(eventName))
            return getPreviousState();
        else
            return this;
    }

    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName)
    {
        if ("method".equals(eventName))
            return new MethodContext(getResultRoot(), this, name, methodId++);
        return this;
    }

    @Override
    public void processTag(String name, Iterator<Attribute> attrs)
    {
        if ("class".equals(name))
        {
            String nameAttr = getNameAttr(attrs);
            if (nameAttr == null || "".equals(nameAttr))
            {
                if (getPreviousState() instanceof ClassContext)
                {
                    String upperName = ((ClassContext)getPreviousState()).getName();
                    int innerCount = ((ClassContext)getPreviousState()).getNextInnerCount();
                    name = upperName + '$' + innerCount;
                }
            }
            else
            {
                if (getPreviousState() instanceof ClassContext)
                    name = ((ClassContext)getPreviousState()).getName() + "." + nameAttr;
                else
                    name = compilationUnit.getPackageName() + nameAttr;
            }
            compilationUnit.addClass(name);
            System.out.println("Found class '" + name + "'");
        }
    }

    @Override
    public void finish(String eventName)
    {

    }
    
    public String getName(){
        return name;
    }
    
    public int getNextInnerCount(){
        return ++innerCount;
    }
    
}
