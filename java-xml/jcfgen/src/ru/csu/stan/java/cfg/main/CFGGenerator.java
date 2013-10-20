package ru.csu.stan.java.cfg.main;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.math.BigInteger;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Unmarshaller;
import javax.xml.stream.XMLEventReader;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.events.XMLEvent;

import ru.csu.stan.java.cfg.automaton.ContextFactory;
import ru.csu.stan.java.cfg.jaxb.Method;
import ru.csu.stan.java.cfg.jaxb.ObjectFactory;
import ru.csu.stan.java.cfg.jaxb.Project;
import ru.csu.stan.java.cfg.util.ImportedClassIdGenerator;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.HandlerFactory;
import ru.csu.stan.java.classgen.handlers.IStaxHandler;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.util.ClassIdGenerator;
import ru.csu.stan.java.classgen.util.IClassIdGenerator;

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
			Classes classes = (Classes) unmarshall.unmarshal(new File(inputUcr));
			idGenerator = ImportedClassIdGenerator.getInstanceImportClasses(classes);
		}
		else
			idGenerator = ClassIdGenerator.getInstance();
	}

	public Project processInputFile(String filename){
		
		Project p = firstPass(filename).getResultRoot();
		secondPass(p);
		return p;
	}
	
	/**
	 * Первый проход генератора CFG. Создает основное дерево элементов для всех методов всех классов.
	 * @param filename
	 * @return
	 */
	private IContext<Project> firstPass(String filename){
		IContext<Project> context = ContextFactory.getStartContext(objectFactory.createProject());
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
				((Method) o).setUcrId(idGenerator.getClassId(method.getParentClass()));
				((Method) o).setCfgId(BigInteger.valueOf(cfgId++));
			}
		}
	}
}
