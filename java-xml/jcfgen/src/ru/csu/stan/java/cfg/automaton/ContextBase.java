package ru.csu.stan.java.cfg.automaton;

import java.util.Iterator;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.cfg.jaxb.ObjectFactory;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.classgen.automaton.IContext;

public abstract class ContextBase implements IContext<Project> {

	private Project resultRoot;
	private ContextBase previousState;
	protected final static String NAME_ATTRIBUTE = "name";
	private static ObjectFactory objectFactory = new ObjectFactory();
	
	ContextBase(Project resultRoot, ContextBase previousState) {
		this.resultRoot = resultRoot;
		this.previousState = previousState;
	}

	protected ContextBase getPreviousState() {
		return previousState;
	}

	@Override
	public Project getResultRoot() {
		return resultRoot;
	}
	
	protected String getNameAttr(Iterator<Attribute> attrs){
        String result = "";
        while (attrs.hasNext()){
            Attribute a = attrs.next();
            if (NAME_ATTRIBUTE.equals(a.getName().toString()))
                return a.getValue();
        }
        return result;
    }
    
    protected String getAttribute(Iterator<Attribute> attrs, String attrName){
        String result = "";
        while (attrs.hasNext()){
            Attribute a = attrs.next();
            if (attrName.equals(a.getName().toString()))
                return a.getValue();
        }
        return result;
    }

    protected static ObjectFactory getObjectFactory()
    {
        return objectFactory;
    }

}
