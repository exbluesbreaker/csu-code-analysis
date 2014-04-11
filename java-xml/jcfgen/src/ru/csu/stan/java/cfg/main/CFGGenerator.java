package ru.csu.stan.java.cfg.main;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.math.BigInteger;
import java.util.Iterator;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Unmarshaller;
import javax.xml.stream.XMLEventReader;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.events.XMLEvent;

import ru.csu.stan.java.cfg.automaton.ContextFactory;
import ru.csu.stan.java.cfg.jaxb.Block;
import ru.csu.stan.java.cfg.jaxb.Call;
import ru.csu.stan.java.cfg.jaxb.Method;
import ru.csu.stan.java.cfg.jaxb.ObjectFactory;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.jaxb.Target;
import ru.csu.stan.java.cfg.jaxb.TargetClass;
import ru.csu.stan.java.cfg.util.ImportedClassIdGenerator;
import ru.csu.stan.java.cfg.util.MethodRegistry;
import ru.csu.stan.java.cfg.util.MethodRegistryItem;
import ru.csu.stan.java.cfg.util.UCFRClassNameResolver;
import ru.csu.stan.java.cfg.util.scope.ScopeRegistry;
import ru.csu.stan.java.cfg.util.scope.VariableFromScope;
import ru.csu.stan.java.cfg.util.scope.VariableScope;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.HandlerFactory;
import ru.csu.stan.java.classgen.handlers.IStaxHandler;
import ru.csu.stan.java.classgen.jaxb.Argument;
import ru.csu.stan.java.classgen.jaxb.Class;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.util.ClassIdGenerator;
import ru.csu.stan.java.classgen.util.IClassIdGenerator;
import ru.csu.stan.java.classgen.util.ImportRegistry;
import ru.csu.stan.java.classgen.util.PackageRegistry;

/**
 * 
 * @author mz
 *
 */
public class CFGGenerator {
	
	private IClassIdGenerator idGenerator;
	private XMLInputFactory xmlFactory;
	private HandlerFactory handlersFactory;
	private ObjectFactory objectFactory;
	private MethodRegistry cfgRegistry;
	private MethodRegistry ucrRegistry;
	private ImportRegistry imports;
	private PackageRegistry packages;
	private Classes classes;
	private UCFRClassNameResolver nameResolver;
	
	private CFGGenerator(){
		xmlFactory = XMLInputFactory.newInstance();
		handlersFactory = HandlerFactory.getInstance();
		objectFactory = new ObjectFactory();
	}
	
	public static CFGGenerator getInstance(){
		return new CFGGenerator();
	}
	
	public void importUcrIds(String inputUcr) throws JAXBException{
		if (inputUcr != null && !"".equals(inputUcr)) {
			JAXBContext jcontext = JAXBContext.newInstance("ru.csu.stan.java.classgen.jaxb");
			Unmarshaller unmarshall = jcontext.createUnmarshaller();
			classes = (Classes) unmarshall.unmarshal(new File(inputUcr));
			idGenerator = ImportedClassIdGenerator.getInstanceImportClasses(classes);
			importMethodregistry(classes);
		}
		else
			idGenerator = ClassIdGenerator.getInstance();
	}
	
	private void importMethodregistry(Classes classes){
		ucrRegistry = MethodRegistry.getInstance();
		for (Class clazz: classes.getClazz()){
			for (ru.csu.stan.java.classgen.jaxb.Method method: clazz.getMethod()){
				MethodRegistryItem item = new MethodRegistryItem();
				item.setName(method.getName());
				item.setId(method.getId().intValue());
				for (Argument arg: method.getArg())
					item.addArg(arg.getName());
				ucrRegistry.addMethodToRegistry(clazz.getName(), item);			
			}
		}
	}

	public Project processInputFile(String filename){
		Project p = firstPass(filename).getResultRoot();
		secondPass(p);
		thirdPass(p);
		return p;
	}
	
	/**
	 * Первый проход генератора CFG. Создает основное дерево элементов для всех методов всех классов.
	 * @param filename
	 * @return
	 */
	private IContext<Project> firstPass(String filename){
		this.cfgRegistry = MethodRegistry.getInstance();
		this.imports = new ImportRegistry();
		this.packages = new PackageRegistry();
		IContext<Project> context = ContextFactory.getStartContext(objectFactory.createProject(), this.cfgRegistry, this.imports, this.packages);
		try{
			File f = new File(filename);
			XMLEventReader reader = xmlFactory.createXMLEventReader(new FileInputStream(f));
			try{
				while (reader.hasNext()){
					XMLEvent nextEvent = reader.nextEvent();
					IStaxHandler<Project> handler = handlersFactory.createHandler(nextEvent);
					context = handler.handle(context);
				}
			}
			finally{
				reader.close();
				this.nameResolver = UCFRClassNameResolver.getInstance(imports, packages);
			}
		}
		catch (FileNotFoundException e) {
			System.out.println("File not found!");
			e.printStackTrace();
		}
		catch (XMLStreamException e) {
			System.out.println("Wrong XML");
			e.printStackTrace();
		}
		return context;
	}
	
	/**
	 * Второй проход генератора CFG. Проставляет ID для методов.
	 * Устанавливает как CFG-ID, так и связанные UCR-ID.
	 * @param project
	 */
	private void secondPass(Project project){
		int cfgId = 1;
		for (Object o: project.getMethodOrFunction()){
			if (o instanceof Method){
				Method method = (Method) o;
				int id = method.getUcrMethodId().intValue();
				MethodRegistryItem item = cfgRegistry.getItem(method.getParentClass(), id);
				MethodRegistryItem ucrItem = ucrRegistry.findSame(method.getParentClass(), item);
				((Method) o).setUcrId(idGenerator.getClassId(method.getParentClass()));
				((Method) o).setCfgId(BigInteger.valueOf(cfgId++));
				if (ucrItem != null)
					((Method) o).setUcrMethodId(BigInteger.valueOf(ucrItem.getId()));
				else
					((Method) o).setUcrMethodId(null);
			}
		}
	}
	
	/**
	 * Третий проход. Устанавливает id для вызовов.
	 * @param project
	 */
	private void thirdPass(Project project){
		for (Object o: project.getMethodOrFunction()){
			if (o instanceof Method){
				Method method = (Method) o;
				VariableScope rootScope = ScopeRegistry.getInstance().findScopeByClass(method.getParentClass());
				for (Object bo: method.getTryExceptOrTryFinallyOrWith()){
					if (bo instanceof Block){
						Block block = (Block) bo;
						for (Iterator<Call> it = block.getCall().iterator();it.hasNext();){
							Call call = it.next();
							String varName = "";
							String callName = "";
							if (call.getGetattr() != null){
								if (call.getGetattr().getLabel().equals("this")){
									String name = call.getGetattr().getName();
									int dotIndex = name.indexOf('.');
									if (dotIndex < 0){
										varName = "this";
										callName = name;
									}
									else{
										varName = name.substring(0, dotIndex);
										call.getGetattr().setLabel("this." + varName);
										String leastName = name.substring(dotIndex + 1, name.length());
										if (leastName.indexOf('.') < 0)
											callName = leastName;
										else
											callName = leastName.substring(0, leastName.indexOf('.'));
										call.getGetattr().setName(callName);
									}
									
								}
								else{
									varName = call.getGetattr().getLabel();
									callName = call.getGetattr().getName();
								}
							}
							if (call.getDirect() != null){
								if (call.getDirect().getTarget() != null)
									varName = "this";
								else
									varName = "";
								callName = call.getDirect().getName();
							}
							VariableFromScope var = getScopedVar(varName, rootScope);
							if (var == null){
								var = getScopedVar(varName, rootScope);
							}
							String fullName = "";
							if (var != null)
								fullName = nameResolver.getFullTypeName(var.getType(), method.getParentClass(), this.classes);
							if ("this".equals(varName))
								fullName = method.getParentClass();
							if ("".equals(varName))
								fullName = nameResolver.getFullTypeName(callName, method.getParentClass(), this.classes);
							if (fullName == null || fullName.isEmpty()){
								if (call.getDirect() != null){
									Target target = new ObjectFactory().createTarget();
									target.setType("method");
									call.getDirect().setTarget(target);
									call.getDirect().setSpaceType("external");
								}
							}
							else{
								if (call.getGetattr() != null){
									TargetClass tc = new ObjectFactory().createTargetClass();
									tc.setUcrId(idGenerator.getClassId(fullName));
									tc.setLabel(fullName);
									Target target = new ObjectFactory().createTarget();
									target.setCfgId(getCfgId(fullName, callName, project));
									target.setType("method");
									target.setTargetClass(tc);
									call.getGetattr().getTarget().add(target);
								}
								if (call.getDirect() != null){
									if ("".equals(varName)){
										TargetClass tc = new ObjectFactory().createTargetClass();
										tc.setUcrId(idGenerator.getClassId(fullName));
										tc.setLabel(fullName);
										Target target = new ObjectFactory().createTarget();
										target.setCfgId(getCfgId(fullName, callName, project));
										target.setType("method");
										target.setTargetClass(tc);
										call.getDirect().setTarget(target);
									}
									else{
										TargetClass tc = new ObjectFactory().createTargetClass();
										tc.setUcrId(method.getUcrId());
										tc.setLabel(method.getParentClass());
										Target target = new ObjectFactory().createTarget();
										target.setCfgId(getCfgId(method.getParentClass(), callName, project));
										target.setType("method");
										target.setTargetClass(tc);
										call.getDirect().setTarget(target);
									}
								}
							}
						}
					}
				}
			}
		}
	}
	
	private BigInteger getCfgId(String fullClassName, String call, Project project){
		for (Object o: project.getMethodOrFunction()){
			if (o instanceof Method){
				Method method = (Method) o;
				if (method.getParentClass().equals(fullClassName) && call.equals(method.getName()))
					return method.getCfgId();
			}
		}
		return null;		
	}
	
	private VariableFromScope getScopedVar(String name, VariableScope rootScope){
		for (VariableFromScope var: rootScope.listVars())
			if (var.getName().equals(name))
				return var;
		for (VariableScope childScope: rootScope.listChildren()){
			VariableFromScope found = getScopedVar(name, childScope);
			if (found != null)
				return found;
		}
		return null;
	}
}
