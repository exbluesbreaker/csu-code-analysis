package ru.csu.stan.java.cfg.automaton;

import java.util.Iterator;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * Состояние анализа компилируемого файла.
 * Собрает всю информацию внутри файла.
 * 
 * @author mzubov
 *
 */
class CompilationUnitContext extends ContextBase
{
    private static final String FILENAME_ATTRIBUTE = "filename";
    private CompilationUnit compilationUnit = new CompilationUnit();

    CompilationUnitContext(Project resultRoot, ContextBase previousState)
    {
        super(resultRoot, previousState);
    }

    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName)
    {
        if ("import".equals(eventName))
            return new ImportContext(getResultRoot(), this, compilationUnit);
        if ("package".equals(eventName))
            return new PackageContext(getResultRoot(), this, compilationUnit);
        if ("class".equals(eventName))
            return new ClassContext(getResultRoot(), this, compilationUnit);
        return this;
    }

    @Override
    public void processTag(String name, Iterator<Attribute> attrs)
    {
        if ("compilation_unit".equals(name)){
            compilationUnit.setFilename(getAttribute(attrs, FILENAME_ATTRIBUTE));
        }
    }

    @Override
    public void finish(String eventName)
    {

    }

    @Override
    public ContextBase getPreviousState(String eventName)
    {
        if ("compilation_unit".equals(eventName))
            return getPreviousState();
        else
            return this;
    }

}
