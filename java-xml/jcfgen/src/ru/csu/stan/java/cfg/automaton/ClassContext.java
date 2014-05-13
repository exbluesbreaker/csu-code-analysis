package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.automaton.base.ContextBase;
import ru.csu.stan.java.cfg.automaton.base.IClassInsidePart;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.util.scope.ScopeRegistry;
import ru.csu.stan.java.cfg.util.scope.VariableScope;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * Состояние анализа класса.
 * 
 * @author mzubov
 *
 */
class ClassContext extends ContextBase implements IClassInsidePart
{
    private String name = "";
    private int innerCount;
    private CompilationUnit compilationUnit;
    private int methodId = 0;
    private VariableScope scope = new VariableScope();

    ClassContext(ContextBase previousState, CompilationUnit compilationUnit)
    {
        super(previousState);
        this.compilationUnit = compilationUnit;
    }

    @Override
    public IContext<Project> getPreviousState(String eventName)
    {
        if ("class".equals(eventName))
            return getUpperState();
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
        if ("variable".equals(eventName))
        	return new VariableContext(this, scope, null, compilationUnit);
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
                if (getUpperState() instanceof IClassInsidePart)
                {
                    String upperName = ((IClassInsidePart)getUpperState()).getClassName();
                    int innerCount = ((IClassInsidePart)getUpperState()).getNextInnerCount();
                    this.name = upperName + '$' + innerCount;
                }
            }
            else
            {
                if (getUpperState() instanceof IClassInsidePart)
                	this.name = ((IClassInsidePart)getUpperState()).getClassName() + "." + nameAttr;
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
    	if ("class".equals(eventName)){
    		scope.setName(this.name);
    		ScopeRegistry.getInstance().addScope(scope);
    		String currentPackage = compilationUnit.getPackageName();
    		getPackageRegistry().addClassToPackage(name.substring(currentPackage.length()+1), currentPackage.substring(0, currentPackage.length()));
    	}
    }
    
    @Override
    public String getClassName(){
        return name;
    }
    
    @Override
    public int getNextInnerCount(){
        return ++innerCount;
    }

	@Override
	public VariableScope getVariableScope() {
		return scope;
	}
    
}
