package ru.csu.stan.java.cfg.automaton;

import java.util.Iterator;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * Состояние анализа имени пакета в файле.
 * 
 * @author mzubov
 *
 */
public class PackageContext extends ContextBase
{
    private CompilationUnit compilationUnit;
    private String currentPackage;

    PackageContext(Project resultRoot, ContextBase previousState, CompilationUnit compilationUnit)
    {
        super(resultRoot, previousState);
        this.compilationUnit = compilationUnit;
    }

    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName)
    {
        return this;
    }

    @Override
    public void processTag(String name, Iterator<Attribute> attrs)
    {
        if ("package".equals(name))
            currentPackage = "";
        if ("member_select".equals(name) || "identifier".equals(name))
            currentPackage = getNameAttr(attrs) + '.' + currentPackage;
    }

    @Override
    public void finish(String eventName)
    {
        if ("package".equals(eventName))
            compilationUnit.setPackageName(currentPackage.substring(0, currentPackage.length()-1));
    }

    @Override
    public ContextBase getPreviousState(String eventName)
    {
        if ("package".equals(eventName))
            return getPreviousState();
        else
            return this;
    }

}
