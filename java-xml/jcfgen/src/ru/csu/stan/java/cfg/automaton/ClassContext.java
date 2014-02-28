package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * Состояние анализа класса.
 * 
 * @author mzubov
 *
 */
class ClassContext extends ContextBase implements IClassNameHolder
{
    private String name = "";
    private int innerCount;
    private CompilationUnit compilationUnit;
    private int methodId = 0;

    ClassContext(ContextBase previousState, CompilationUnit compilationUnit)
    {
        super(previousState);
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
            return new MethodContext(this, name, compilationUnit, ++methodId);
        if ("class".equals(eventName))
            return new ClassContext(this, compilationUnit);
        return this;
    }

    @Override
    public void processTag(String name, NodeAttributes attrs)
    {
        if ("class".equals(name))
        {
            String nameAttr = attrs.getNameAttribute();
            if (nameAttr == null || "".equals(nameAttr))
            {
                if (getPreviousState() instanceof IClassNameHolder)
                {
                    String upperName = ((IClassNameHolder)getPreviousState()).getClassName();
                    int innerCount = ((IClassNameHolder)getPreviousState()).getNextInnerCount();
                    this.name = upperName + '$' + innerCount;
                }
            }
            else
            {
                if (getPreviousState() instanceof IClassNameHolder)
                	this.name = ((IClassNameHolder)getPreviousState()).getClassName() + "." + nameAttr;
                else
                	this.name = compilationUnit.getPackageName() + "." + nameAttr;
            }
            compilationUnit.addClass(this.name);
            System.out.println("Found class '" + this.name + "'");
        }
    }

    @Override
    public void finish(String eventName)
    {

    }
    
    @Override
    public String getClassName(){
        return name;
    }
    
    @Override
    public int getNextInnerCount(){
        return ++innerCount;
    }
    
}
