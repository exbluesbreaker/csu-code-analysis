package ru.csu.stan.java.cfg.automaton;

import ru.csu.stan.java.cfg.automaton.base.ContextBase;
import ru.csu.stan.java.cfg.automaton.base.ControlFlowForkContextBase;
import ru.csu.stan.java.cfg.automaton.base.FlowCursor;
import ru.csu.stan.java.cfg.jaxb.If;
import ru.csu.stan.java.cfg.jaxb.Method;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.NodeAttributes;
import ru.csu.stan.java.classgen.util.CompilationUnit;

/**
 * 
 * @author mz
 *
 */
class IfContext extends ControlFlowForkContextBase<If>{
	
    private FlowCursor thenCursor;
    private FlowCursor elseCursor;

    IfContext(ContextBase previousState, FlowCursor cursor, CompilationUnit compilationUnit, Method method){
        super(previousState, cursor, compilationUnit, method);
    }


    @Override
    public IContext<Project> getNextState(IContext<Project> context, String eventName)
    {
        if ("then_part".equals(eventName)){
        	thenCursor = new FlowCursor();
        	return createStandardControlFlowContext(thenCursor);
        }
        if ("else_part".equals(eventName)){
            elseCursor = getCursor().clone();
            elseCursor.addParentId(getFlowForkBlock().getId().intValue());
            if (thenCursor != null)
                elseCursor.setCurrentId(thenCursor.getCurrentId());
            return new ControlFlowContext(this, getMethod(), elseCursor, getCompilationUnit());
        }
        return this;
    }

    @Override
    public void processTag(String name, NodeAttributes attrs)
    {
    	super.processTag(name, attrs);
        if ("condition".equals(name)){
            if (getFlowForkBlock() != null)
            	getFlowForkBlock().setTest("condition");
        }
    }
    

    @Override
    public void finish(String eventName){
        if (isEventFitToContext(eventName)){
            addCursorDataToCurrent(thenCursor);
            if (elseCursor != null)
            	addCursorDataToCurrent(elseCursor);
            else
            	getCursor().addParentId(getFlowForkBlock().getId().intValue());
        }
    }


	@Override
	protected If createFlowForkBlock() {
		return getObjectFactory().createIf();
	}


	@Override
	protected String[] getTagNames() {
		return new String[] {"if"};
	}

}
