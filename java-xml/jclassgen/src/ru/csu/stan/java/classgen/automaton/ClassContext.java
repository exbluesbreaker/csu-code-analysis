package ru.csu.stan.java.classgen.automaton;

import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Stack;

import javax.xml.stream.events.Attribute;

import ru.csu.stan.java.classgen.jaxb.AggregatedType;
import ru.csu.stan.java.classgen.jaxb.Argument;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.jaxb.CommonType;
import ru.csu.stan.java.classgen.jaxb.Method;
import ru.csu.stan.java.classgen.jaxb.ModifierType;
import ru.csu.stan.java.classgen.jaxb.ObjectFactory;
import ru.csu.stan.java.classgen.jaxb.ParentClass;
import ru.csu.stan.java.classgen.util.ClassIdGenerator;
import ru.csu.stan.java.classgen.util.CompilationUnit;
import ru.csu.stan.java.classgen.util.ImportRegistry;
import ru.csu.stan.java.classgen.util.PackageRegistry;

/**
 * Контекст анализа AST для получения классового представления.
 * Представляет собой конечный автомат со стековой памятью.
 * В новое состояние переходит явным указанием такового,
 * а выходит из него возвратом к предыдущему.
 * 
 * @author mz
 *
 */
public class ClassContext extends ContextBase {

	private String currentPackage;
	private String currentImport;
	private String currentNewClass;
	private CompilationUnit currentUnit = new CompilationUnit();
	private Stack<ru.csu.stan.java.classgen.jaxb.Class> classStack = new Stack<ru.csu.stan.java.classgen.jaxb.Class>();
	private Stack<Integer> classInnersCount = new Stack<Integer>();
	private ru.csu.stan.java.classgen.jaxb.Attribute currentAttribute;
	private Stack<Method> methodStack = new Stack<Method>();
	private ParentClass currentParent;
	private Argument currentArgument;
	private List<ModifierType> currentModifier = new LinkedList<ModifierType>();
	private Map<String, String> imported = new HashMap<String, String>();
	private Stack<ContextState> stateStack = new Stack<ContextState>();
	private CommonType currentCommonType;
	private AggregatedType currentAggregatedType;
	private boolean currentTypeAggregated = false;
	
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
	
	@Override
	public Classes getResultRoot() {
		return root;
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
	
	public void setResultTypeState(){
		stateStack.push(ContextState.RETURN_TYPE);
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
		if (state == ContextState.ARGUMENT)
			stateStack.push(ContextState.ARG_TYPE);
	}
	
	public void setPreviousVarState(){
		ContextState state = stateStack.peek();
		if (state == ContextState.FIELD || state == ContextState.ARGUMENT)
			stateStack.pop();
	}
	
	public void setPreviousVartypeState(){
		ContextState state = stateStack.peek();
		if (state == ContextState.FIELD_TYPE || state == ContextState.ARG_TYPE)
			stateStack.pop();
	}
	
	public void setPreviousState(){
		stateStack.pop();
	}
	
	@Override
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
				processTypeTag(name, attrs);
				break;
			case RETURN_TYPE:
				processTypeTag(name, attrs);
				break;
			case ARG_TYPE:
				processTypeTag(name, attrs);
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
				classStack.peek().getMethod().add(methodStack.pop());
				break;
			case FIELD:
				classStack.peek().getAttr().add(currentAttribute);
				currentAttribute = null;
				break;
			case ARGUMENT:
				methodStack.peek().getArg().add(currentArgument);
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
					if (!methodStack.isEmpty())
						methodStack.peek().getModifier().addAll(currentModifier);
				if (stateStack.peek() == ContextState.FIELD)
					currentAttribute.getModifier().addAll(currentModifier);
				stateStack.push(currentState);
				currentModifier.clear();
				break;
			case FIELD_TYPE:
				if (currentCommonType != null)
					currentAttribute.getCommonType().add(currentCommonType);
				if (currentAggregatedType != null)
					currentAttribute.getAggregatedType().add(currentAggregatedType);
				currentCommonType = null;
				currentAggregatedType = null;
				currentTypeAggregated = false;
				break;
			case RETURN_TYPE:
				if (currentCommonType != null)
					if (!methodStack.isEmpty())
						methodStack.peek().getCommonType().add(currentCommonType);
				if (currentAggregatedType != null)
					if (!methodStack.isEmpty())
						methodStack.peek().getAggregatedType().add(currentAggregatedType);
				currentCommonType = null;
				currentAggregatedType = null;
				currentTypeAggregated = false;
				break;
			case ARG_TYPE:
				if (currentCommonType != null)
					currentArgument.getCommonType().add(currentCommonType);
				if (currentAggregatedType != null)
					currentArgument.getAggregatedType().add(currentAggregatedType);
				currentCommonType = null;
				currentAggregatedType = null;
				currentTypeAggregated = false;
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
		if (state == ContextState.ARG_TYPE)
			finish();
	}
	
	public void finishIdentifier(){
		if (stateStack.peek() == ContextState.PARENT){
			classStack.peek().getParent().add(currentParent);
			currentParent = factory.createParentClass();
		}
		if (stateStack.peek() == ContextState.ARG_TYPE || stateStack.peek() == ContextState.RETURN_TYPE || stateStack.peek() == ContextState.FIELD_TYPE)
			if (currentTypeAggregated){
				
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
			Method currentMethod = factory.createMethod();
			String nameAttr = getNameAttr(attrs);
			if ("<init>".equals(nameAttr))
				nameAttr = classStack.peek().getName().substring(classStack.peek().getName().lastIndexOf('.')+1);
			currentMethod.setName(nameAttr);
			methodStack.push(currentMethod);
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
	
	private void processTypeTag(String name, Iterator<Attribute> attrs){
		if ("member_select".equals(name) || "identifier".equals(name)){
			if (currentAggregatedType == null){
				if (currentCommonType == null)
				{
					currentCommonType = factory.createCommonType();
					currentCommonType.setName("");
				}
				if (currentCommonType.getName().isEmpty())
					currentCommonType.setName(getNameAttr(attrs));
				else
					currentCommonType.setName(getNameAttr(attrs) + '.' + currentCommonType.getName());
			}
			else{
				if (currentTypeAggregated){
					if (currentAggregatedType.getElementType().isEmpty())
						currentAggregatedType.setElementType(getNameAttr(attrs));
					else
						currentAggregatedType.setElementType(getNameAttr(attrs) + '.' + currentAggregatedType.getElementType());
				}
				else{
					if (currentAggregatedType.getName().isEmpty())
						currentAggregatedType.setName(getNameAttr(attrs));
					else
						currentAggregatedType.setName(getNameAttr(attrs) + '.' + currentAggregatedType.getName());
				}
			}
		}
		if ("parameterized_type".equals(name) && currentCommonType == null){
			if (currentAggregatedType == null){
				currentAggregatedType = factory.createAggregatedType();
				currentAggregatedType.setName("");
				currentAggregatedType.setElementType("");
			}
		}
		if ("arguments".equals(name)){
			currentTypeAggregated = true;
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

	@Override
	public IContext<Classes> getNextState(IContext<Classes> context, String eventName) {
		if (eventName.equals("package")){
			this.setPackageState();
		}
		if (eventName.equals("class")){
			this.setClassState();
		}
		if (eventName.equals("method")){
			this.setMethodState();
		}
		if (eventName.equals("variable")){
			this.setStateForVar();
		}
		if (eventName.equals("extends") || 
				eventName.equals("implements")){
			this.setParentState();
		}
		if (eventName.equals("import")){
			this.setImportState();
		}
		if (eventName.equals("block")){
			this.setEmptyState();
		}
		if (eventName.equals("new_class")){
			this.setNewClassState();
		}
//		if (eventName.equals("arguments")){
//			context.setEmptyState();
//		}
		if (eventName.equals("compilation_unit")){
			this.setCompilationUnitState();
		}
		if (eventName.equals("modifiers")){
			this.setModifierState();
		}
		if (eventName.equals("vartype")){
			this.setVartypeState();
		}
		if (eventName.equals("resulttype")){
			this.setResultTypeState();
		}
		return this;
	}

	@Override
	public IContext<Classes> getPreviousState(String eventName) {
		if (eventName.equals("package") ||
			eventName.equals("class") ||
			eventName.equals("method") ||
			eventName.equals("extends") || 
			eventName.equals("implements") ||
			eventName.equals("import") ||
			eventName.equals("block") ||
			eventName.equals("new_class") ||
//					event.getName().toString().equals("arguments") ||
			eventName.equals("modifiers") ||
			eventName.equals("resulttype") ||
			eventName.equals("compilation_unit") ){
			this.setPreviousState();
		}
		
		if (eventName.equals("variable"))
		{
			this.setPreviousVarState();
		}
				
		if (eventName.equals("vartype"))
		{
			this.setPreviousVartypeState();
		}
		return this;
	}

	@Override
	public void finish(String eventName) {
		if (eventName.equals("package") ||
			eventName.equals("class") ||
			eventName.equals("method") ||
			eventName.equals("extends") || 
			eventName.equals("implements") ||
			eventName.equals("import") ||
			eventName.equals("block") ||
			eventName.equals("new_class") ||
//				event.getName().toString().equals("arguments") ||
			eventName.equals("modifiers") ||
			eventName.equals("resulttype") ||
			eventName.equals("compilation_unit") ){
			this.finish();
		}
		
		if (eventName.equals("variable"))
		{
			this.finishVar();
		}
		
		if (eventName.equals("identifier"))
			this.finishIdentifier();
		
		if (eventName.equals("vartype"))
		{
			this.finishVartype();
		}
	}
}
