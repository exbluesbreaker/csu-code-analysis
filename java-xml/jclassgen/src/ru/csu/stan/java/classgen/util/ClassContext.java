package ru.csu.stan.java.classgen.util;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Stack;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.classgen.jaxb.Argument;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.jaxb.Method;
import ru.csu.stan.java.classgen.jaxb.ObjectFactory;
import ru.csu.stan.java.classgen.jaxb.ParentClass;

/**
 * Контекст анализа AST для получения классового представления
 * 
 * @author mz
 *
 */
public class ClassContext {

	private Classes root;
	private String currentPackage;
	private String currentImport;
	private Stack<ru.csu.stan.java.classgen.jaxb.Class> classStack = new Stack<ru.csu.stan.java.classgen.jaxb.Class>();
	private Stack<Integer> classInnersCount = new Stack<Integer>();
	private ru.csu.stan.java.classgen.jaxb.Attribute currentAttribute;
	private Method currentMethod;
	private ParentClass currentParent;
	private Argument currentArgument;
	private ObjectFactory factory;
	private Map<String, String> imported = new HashMap<String, String>();
	private Stack<ContextState> stateStack = new Stack<ContextState>();
	
	private ClassContext() {}
	
	private ClassContext(Classes classes, ObjectFactory factory) {
		this.root = classes;
		this.factory = factory;
		stateStack.push(ContextState.EMPTY);
	}
	
	public static ClassContext getInstance(Classes classes, ObjectFactory factory){
		return new ClassContext(classes, factory);
	}
	
	public void setPackageState(){
		stateStack.push(ContextState.PACKAGE);
	}
	
	public void setClassState(){
		stateStack.push(ContextState.CLASS);
	}
	
	public void setFieldState(){
		stateStack.push(ContextState.FIELD);
	}
	
	public void setMethodState(){
		stateStack.push(ContextState.METHOD);
	}
	
	public void setArgumentState(){
		stateStack.push(ContextState.ARGUMENT);
	}
	
	public void setParentState(){
		stateStack.push(ContextState.PARENT);
	}
	
	public void setEmptyState(){
		stateStack.push(ContextState.EMPTY);
	}
	
	public void setImportState(){
		stateStack.push(ContextState.IMPORT);
	}
	
	public void setStateForVar(){
		ContextState state = stateStack.peek();
		if (state == ContextState.CLASS)
			stateStack.push(ContextState.FIELD);
		if (state == ContextState.METHOD)
			stateStack.push(ContextState.ARGUMENT);
	}
	
	public void setPreviousVarState(){
		ContextState state = stateStack.peek();
		if (state == ContextState.FIELD || state == ContextState.ARGUMENT)
			stateStack.pop();
	}
	
	public void setPreviousState(){
		stateStack.pop();
	}
	
	public void processTag(String name, Iterator<Attribute> attrs){
		switch (this.stateStack.peek()){
			case CLASS:
				processClassTag(name, attrs);
				break;
			case METHOD:
				processMethodTag(name, attrs);
				break;
			case FIELD:
				processFieldTag(name, attrs);
				break;
			case ARGUMENT:
				processArgumentTag(name, attrs);
				break;
			case PARENT:
				processParentTag(name, attrs);
				break;
			case PACKAGE:
				processPackageTag(name, attrs);
				break;
			case IMPORT:
				processImportTag(name, attrs);
				break;
			case EMPTY:
				break;
		}
	}
	
	public void finish(){
		switch (this.stateStack.peek()){
			case CLASS:
				root.getClazz().add(classStack.pop());
				classInnersCount.pop();
				break;
			case METHOD:
				classStack.peek().getMethod().add(currentMethod);
				currentMethod = null;
				break;
			case FIELD:
				classStack.peek().getAttr().add(currentAttribute);
				currentAttribute = null;
				break;
			case ARGUMENT:
				currentMethod.getArg().add(currentArgument);
				currentArgument = null;
				break;
			case PARENT:
				if (!imported.containsKey(currentParent.getName().substring(currentParent.getName().lastIndexOf('.')+1, currentParent.getName().length())))
					currentParent.setId(ClassIdGenerator.getInstance().getClassId(currentParent.getName()));
				classStack.peek().getParent().add(currentParent);
				currentParent = null;
				break;
			case IMPORT:
				imported.put(currentImport.substring(currentImport.lastIndexOf('.')+1, currentImport.length()), currentImport);
			default:
				break;
		}
	}
	
	public void finishVar(){
		ContextState state = stateStack.peek();
		if (state == ContextState.FIELD || state == ContextState.ARGUMENT)
			finish();
	}
	
	private void processPackageTag(String name, Iterator<Attribute> attrs){
		if ("package".equals(name))
			currentPackage = "";
		if ("member_select".equals(name) || "identifier".equals(name))
			currentPackage = getNameAttr(attrs) + '.' + currentPackage;
	}
	
	private void processClassTag(String name, Iterator<Attribute> attrs){
		if ("class".equals(name))
		{
			ru.csu.stan.java.classgen.jaxb.Class newClass = factory.createClass();
			String nameAttr = getNameAttr(attrs);
			if (nameAttr == null || "".equals(nameAttr))
			{
				String upperName = classStack.get(classStack.size() - 1).getName();
				int innerCount = classInnersCount.pop().intValue() + 1;
				newClass.setName(upperName + '$' + innerCount);
				classInnersCount.push(Integer.valueOf(innerCount));
			}
			else
				newClass.setName(currentPackage + nameAttr);
			imported.put(nameAttr, newClass.getName());
			newClass.setId(ClassIdGenerator.getInstance().getClassId(newClass.getName()));
			classStack.push(newClass);
			classInnersCount.push(0);
		}
	}
	
	private void processFieldTag(String name, Iterator<Attribute> attrs){
		if ("variable".equals(name))
		{
			currentAttribute = factory.createAttribute();
			currentAttribute.setName(getNameAttr(attrs));
		}
	}
	
	private void processMethodTag(String name, Iterator<Attribute> attrs){
		if ("method".equals(name))
		{
			currentMethod = factory.createMethod();
			currentMethod.setName(getNameAttr(attrs));
		}
	}
	
	private void processArgumentTag(String name, Iterator<Attribute> attrs){
		if ("variable".equals(name))
		{
			currentArgument = factory.createArgument();
			currentArgument.setName(getNameAttr(attrs));
		}
	}
	
	private void processParentTag(String name, Iterator<Attribute> attrs){
		if ("extends".equals(name) || "implements".equals(name))
			currentParent = factory.createParentClass();
		if ("member_select".equals(name))
			currentParent.setName(getNameAttr(attrs) + '.' + currentParent.getName());
		if ("identifier".equals(name))
			if (currentParent.getName() == null || "".equals(currentParent.getName()))
				currentParent.setName(imported.get(getNameAttr(attrs)));
			else
				currentParent.setName(getNameAttr(attrs) + '.' + currentParent.getName());
	}
	
	private void processImportTag(String name, Iterator<Attribute> attrs){
		if ("import".equals(name))
			currentImport = "";
		if ("member_select".equals(name) || "identifier".equals(name))
			if ("".equals(currentImport))
				currentImport = getNameAttr(attrs);
			else
				currentImport = getNameAttr(attrs) + '.' + currentImport;
	}
	
	private String getNameAttr(Iterator<Attribute> attrs){
		String result = "";
		while (attrs.hasNext()){
			Attribute a = attrs.next();
			if ("name".equals(a.getName().toString()))
				return a.getValue();
		}
		return result;
	}
}
