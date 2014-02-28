package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
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

    ImportContext(ContextBase previousState, CompilationUnit compilationUnit)
    {
        super(previousState);
        this.compilationUnit = compilationUnit;
    }

    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName)
    {
        return this;
    }

    @Override
    public void processTag(String name, NodeAttributes attrs)
    {
        if ("import".equals(name))
            currentImport = "";
        if ("member_select".equals(name) || "identifier".equals(name))
            if ("".equals(currentImport))
                currentImport = attrs.getNameAttribute();
            else
                currentImport = attrs.getNameAttribute() + '.' + currentImport;
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
