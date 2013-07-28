package ru.csu.stan.java.cfg.automaton;

import java.util.Iterator;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * Состояние анализа строки импорта.
 * Записывает в текущий файл указаный в нем импорт.
 * 
 * @author mzubov
 *
 */
class ImportContext extends ContextBase
{
    private CompilationUnit compilationUnit = new CompilationUnit();
    private String currentImport;

    ImportContext(Project resultRoot, ContextBase previousState, CompilationUnit compilationUnit)
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
        if ("import".equals(name))
            currentImport = "";
        if ("member_select".equals(name) || "identifier".equals(name))
            if ("".equals(currentImport))
                currentImport = getNameAttr(attrs);
            else
                currentImport = getNameAttr(attrs) + '.' + currentImport;
    }

    @Override
    public void finish(String eventName)
    {
        if ("import".equals(eventName)){
            compilationUnit.addImport(currentImport);
        }
    }

    @Override
    public ContextBase getPreviousState(String eventName)
    {
        if ("import".equals(eventName))
            return getPreviousState();
        else
            return this;
    }

}