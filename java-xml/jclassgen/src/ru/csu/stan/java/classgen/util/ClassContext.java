package ru.csu.stan.java.classgen.util;

import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Stack;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.classgen.jaxb.Argument;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.jaxb.CommonType;
import ru.csu.stan.java.classgen.jaxb.Method;
import ru.csu.stan.java.classgen.jaxb.ModifierType;
import ru.csu.stan.java.classgen.jaxb.ObjectFactory;
import ru.csu.stan.java.classgen.jaxb.ParentClass;

/**
 * Контекст анализа AST для получения классового представления.
 * Представляет собой конечный автомат со стековой памятью.
 * В новое состояние переходит явным указанием такового,
 * а выходит из него возвратом к предыдущему.
 * 
 * @author mz
 *
 */
public class ClassContext {

	private Classes root;
	private String currentPackage;
	private String currentImport;
	private String currentNewClass;
	private CompilationUnit currentUnit = new CompilationUnit();
	private Stack<ru.csu.stan.java.classgen.jaxb.Class> classStack = new Stack<ru.csu.stan.java.classgen.jaxb.Class>();
	private Stack<Integer> classInnersCount = new Stack<Integer>();
	private ru.csu.stan.java.classgen.jaxb.Attribute currentAttribute;
	private Method currentMethod;
	private ParentClass currentParent;
	private Argument currentArgument;
	private List<ModifierType> currentModifier = new LinkedList<ModifierType>();
	private ObjectFactory factory;
	private Map<String, String> imported = new HashMap<String, String>();
	private Stack<ContextState> stateStack = new Stack<ContextState>();
	private CommonType currentType;
	
	private PackageRegistry packageReg = new PackageRegistry();
	
	public PackageRegistry getPackageReg() {
		return packageReg;
	}

	private ImportRegistry impReg = new ImportRegistry();
	
	public ImportRegistry getImpReg() {
		return impReg;
	}
	
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
	
	public void setNewClassState(){
		stateStack.push(ContextState.NEW_CLASS);
	}
	
	public void setCompilationUnitState(){
		stateStack.push(ContextState.COMPILATION_UNIT);
	}
	
	public void setModifierState(){
		stateStack.push(ContextState.MODIFIERS);
	}
	
	public void setStateForVar(){
		ContextState state = stateStack.peek();
		if (state == ContextState.CLASS)
			stateStack.push(ContextState.FIELD);
		if (state == ContextState.METHOD)
			stateStack.push(ContextState.ARGUMENT);
	}
	
	public void setVartypeState(){
		ContextState state = stateStack.peek();
		if (state == ContextState.FIELD)
			stateStack.push(ContextState.FIELD_TYPE);
	}
	
	public void setPreviousVarState(){
		ContextState state = stateStack.peek();
		if (state == ContextState.FIELD || state == ContextState.ARGUMENT)
			stateStack.pop();
	}
	
	public void setPreviousVartypeState(){
		ContextState state = stateStack.peek();
		if (state == ContextState.FIELD_TYPE)
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
			case NEW_CLASS:
				processNewClass(name, attrs);
				break;
			case MODIFIERS:
				processModifierTag(name, attrs);
				break;
			case FIELD_TYPE:
				processFieldTypeTag(name, attrs);
				break;
			case EMPTY:
				break;
			default:
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
//				if (!imported.containsKey(currentParent.getName().substring(currentParent.getName().lastIndexOf('.')+1, currentParent.getName().length())))
//					currentParent.setId(ClassIdGenerator.getInstance().getClassId(currentParent.getName()));
//				classStack.peek().getParent().add(currentParent);
//				currentParent = null;
				break;
			case IMPORT:
				if (currentImport.indexOf('*') < 0)
					imported.put(currentImport.substring(currentImport.lastIndexOf('.')+1, currentImport.length()), currentImport);
				else
					imported.put(currentImport, currentImport);
				currentUnit.addImport(currentImport);
				currentImport = null;
				break;
			case NEW_CLASS:
				currentNewClass = null;
				break;
			case COMPILATION_UNIT:
				imported.clear();
				currentUnit.setPackageName(currentPackage.substring(0, currentPackage.length()-1));
				currentPackage = null;
				impReg.addCompilationUni(currentUnit);
				currentUnit = new CompilationUnit();
				break;
			case MODIFIERS:
				ContextState currentState = stateStack.pop();
				if (stateStack.peek() == ContextState.CLASS)
					classStack.peek().getModifier().addAll(currentModifier);
				if (stateStack.peek() == ContextState.METHOD)
					currentMethod.getModifier().addAll(currentModifier);
				if (stateStack.peek() == ContextState.FIELD)
					currentAttribute.getModifier().addAll(currentModifier);
				stateStack.push(currentState);
				currentModifier.clear();
				break;
			case FIELD_TYPE:
				if (currentType != null)
					currentAttribute.getCommonType().add(currentType);
				currentType = null;
				break;
			default:
				break;
		}
	}
	
	public void finishVar(){
		ContextState state = stateStack.peek();
		if (state == ContextState.FIELD || state == ContextState.ARGUMENT)
			finish();
	}
	
	public void finishVartype(){
		ContextState state = stateStack.peek();
		if (state == ContextState.FIELD_TYPE)
			finish();
	}
	
	public void finishIdentifier(){
		if (stateStack.peek() == ContextState.PARENT){
			classStack.peek().getParent().add(currentParent);
			currentParent = factory.createParentClass();
		}
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
			{
				if (!classStack.isEmpty())
					newClass.setName(classStack.peek().getName() + "." + nameAttr);
				else
					newClass.setName(currentPackage + nameAttr);
			}
			if (currentNewClass != null)
			{
				ParentClass parent = factory.createParentClass();
				if (!imported.containsKey(currentNewClass))
					parent.setName(currentNewClass);
				else
					parent.setName(imported.get(currentNewClass));
//				parent.setId(ClassIdGenerator.getInstance().getClassId(parent.getName()));
				newClass.getParent().add(parent);
			}
			imported.put(newClass.getName().substring(currentPackage.length()), newClass.getName());
			packageReg.addClassToPackage(newClass.getName().substring(currentPackage.length()), currentPackage.substring(0, currentPackage.length()-1));
			newClass.setId(ClassIdGenerator.getInstance().getClassId(newClass.getName()));
			currentUnit.addClass(newClass.getName());
			System.out.println("Found class '" + newClass.getName() + "'");
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
			String nameAttr = getNameAttr(attrs);
			if ("<init>".equals(nameAttr))
				nameAttr = classStack.peek().getName().substring(classStack.peek().getName().lastIndexOf('.')+1);
			currentMethod.setName(nameAttr);
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
			{
				String nameAttr = getNameAttr(attrs);
				if (imported.containsKey(nameAttr))
					currentParent.setName(imported.get(nameAttr));
				else
					currentParent.setName(nameAttr);
			}
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
	
	private void processNewClass(String name, Iterator<Attribute> attrs){
		if ("new_class".equals(name))
			currentNewClass = "";
		if ("member_select".equals(name) || "identifier".equals(name))
			if ("".equals(currentNewClass))
				currentNewClass = getNameAttr(attrs);
			else
				currentNewClass = getNameAttr(attrs) + '.' + currentNewClass;
	}
	
	private void processModifierTag(String name, Iterator<Attribute> attrs){
		if ("modifier".equals(name)){
			ModifierType mod = factory.createModifierType();
			mod.setName(getNameAttr(attrs));
			if (currentModifier == null)
				currentModifier = new LinkedList<ModifierType>();
			currentModifier.add(mod);
		}
	}
	
	private void processFieldTypeTag(String name, Iterator<Attribute> attrs){
		if ("member_select".equals(name) || "identifier".equals(name)){
			if (currentType == null)
			{
				currentType = factory.createCommonType();
				currentType.setName("");
			}
			if (currentType.getName().isEmpty())
				currentType.setName(getNameAttr(attrs));
			else
				currentType.setName(currentType.getName() + '.' + getNameAttr(attrs));
		}
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
