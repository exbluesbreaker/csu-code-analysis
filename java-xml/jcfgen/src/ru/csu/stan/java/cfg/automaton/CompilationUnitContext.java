package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
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

    CompilationUnitContext(ContextBase previousState)
    {
        super(previousState);
    }

    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName)
    {
        if ("import".equals(eventName))
            return new ImportContext(this, compilationUnit);
        if ("package".equals(eventName))
            return new PackageContext(this, compilationUnit);
        if ("class".equals(eventName))
            return new ClassContext(this, compilationUnit);
        return this;
    }

    @Override
    public void processTag(String name, NodeAttributes attrs)
    {
        if ("compilation_unit".equals(name)){
            compilationUnit.setFilename(attrs.getStringAttribute(FILENAME_ATTRIBUTE));
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
