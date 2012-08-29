package ru.csu.stan.java.classgen.main;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.Set;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;
import javax.xml.stream.XMLEventReader;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.events.XMLEvent;

import ru.csu.stan.java.classgen.handlers.HandlerFactory;
import ru.csu.stan.java.classgen.handlers.IStaxHandler;
import ru.csu.stan.java.classgen.jaxb.Class;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.jaxb.ObjectFactory;
import ru.csu.stan.java.classgen.jaxb.ParentClass;
import ru.csu.stan.java.classgen.util.ClassContext;
import ru.csu.stan.java.classgen.util.ClassIdGenerator;
import ru.csu.stan.java.classgen.util.CompilationUnit;
import ru.csu.stan.java.classgen.util.ImportRegistry;
import ru.csu.stan.java.classgen.util.PackageRegistry;

/**
 * Генератор универсального классового представления
 * по AST-представлению Java-кода.
 * Точка входа.
 * 
 * @author mz
 *
 */
public class Main {
	
	private static final String HELP = "USAGE: Main <input file> <output file>";
	
	/**
	 * Точка входа
	 * @param args
	 */
	public static void main(String[] args) {
		if (args != null && args.length > 0 && args.length < 3){
			final String input = args[0];
			final String output = args[1];
			System.out.println("Start working with " + input + " as input file");
			ObjectFactory factory = new ObjectFactory();
			Classes result = factory.createClasses();
			HandlerFactory handlers = HandlerFactory.getInstance();
			XMLInputFactory xmlFactory = XMLInputFactory.newInstance();
			ClassContext context = ClassContext.getInstance(result, factory);
			try{
				File f = new File(input);
				XMLEventReader reader = xmlFactory.createXMLEventReader(new FileInputStream(f));
				try{
					while (reader.hasNext()){
						XMLEvent nextEvent = reader.nextEvent();
						IStaxHandler handler = handlers.createHandler(nextEvent);
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
			
			System.out.println("Resolving parent classes");
			ImportRegistry imports = context.getImpReg();
			PackageRegistry packages = context.getPackageReg();
			for (Class clazz : result.getClazz()){
				CompilationUnit unit = imports.findUnitByClass(clazz.getName());
				Set<String> starImports = unit.getStarImports();
				for (String starImport : starImports){
					Set<String> starClasses = packages.getPackageClasses(starImport.substring(0, starImport.length()-2));
					
				}
			}
			
			System.out.println("Generating IDs for classes");
			for (Class clazz : result.getClazz()){
				if (clazz.getParent() != null)
					for (ParentClass parent : clazz.getParent())
						parent.setId(ClassIdGenerator.getInstance().getClassId(parent.getName()));
			}
			
			try {
				JAXBContext jcontext = JAXBContext.newInstance("ru.csu.stan.java.classgen.jaxb");
				Marshaller marshaller = jcontext.createMarshaller();
				marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true);
				System.out.println("Writing result to " + output);
				marshaller.marshal(result, new File(output));
			} 
			catch (JAXBException e) {
				e.printStackTrace();
			}
		}
		else
			System.out.println(HELP);
	}

}
