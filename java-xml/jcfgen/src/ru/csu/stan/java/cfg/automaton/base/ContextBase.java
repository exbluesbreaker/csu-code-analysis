package ru.csu.stan.java.cfg.automaton.base;

import java.util.Iterator;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.cfg.jaxb.ObjectFactory;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.util.MethodRegistry;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.util.ImportRegistry;
import ru.csu.stan.java.classgen.util.PackageRegistry;

/**
 * Базовый контекст (состояние автомата).
 * Описывает общие поля и методы для всех состояний.
 * 
 * @author mz
 *
 */
public abstract class ContextBase implements IContext<Project> {

	private Project resultRoot;
	private ContextBase previousState;
	protected final static String NAME_ATTRIBUTE = "name";
	private static ObjectFactory objectFactory = new ObjectFactory();
	private MethodRegistry registry;
	private ImportRegistry imports;
	private PackageRegistry packages;
	
	protected ContextBase(ContextBase previousState) {
		this.resultRoot = previousState.getResultRoot();
		this.previousState = previousState;
		this.registry = previousState.getMethodRegistry();
		this.imports = previousState.getImportRegistry();
		this.packages = previousState.getPackageRegistry();
	}
	
	protected ContextBase(Project resultRoot, MethodRegistry registry, ImportRegistry imports, PackageRegistry packages){
		this.resultRoot = resultRoot;
		this.previousState = null;
		this.registry = registry;
		this.imports = imports;
		this.packages = packages;
	}

	public ContextBase getUpperState() {
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

    public MethodRegistry getMethodRegistry() {
		return registry;
	}
    
    public ImportRegistry getImportRegistry(){
    	return imports;
    }
    
    public PackageRegistry getPackageRegistry(){
    	return packages;
    }
}
