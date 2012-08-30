package ru.csu.stan.java.classgen.main;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
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
				// формируем новый список родителей
				List<ParentClass> newParents = new LinkedList<ParentClass>();
				for (ParentClass parent : clazz.getParent()){
					// все по простому: родитель нормально импортирован из проекта
					if (packages.isClassInRegistry(parent.getName()))
						newParents.add(parent);
					// всякие сложности
					else{
						CompilationUnit unit = imports.findUnitByClass(clazz.getName());
						boolean found = false;
						for (String starImport : unit.getStarImports()){
							// отбрасываем ".*"
							Set<String> classesFromStarPackage = packages.getPackageClasses(starImport.substring(0, starImport.length()-3));
							for (String cl: classesFromStarPackage)
								if (cl.endsWith(parent.getName()) && cl.charAt(cl.lastIndexOf(parent.getName())) == '.'){
									parent.setName(cl);
									newParents.add(parent);
									found = true;
									break;
								}
							if (found)
								break;
						}
						if (!found){
							String localClassName = clazz.getName().substring(unit.getPackageName().length()-1);
							if (localClassName.indexOf('.') > 0){
								Set<String> sameThings = new HashSet<String>();
								for (String imp : unit.getImports())
									sameThings.addAll(packages.getClassesByPrefixAndPostfix(imp, parent.getName()));
								if (sameThings.size() > 1){
									String fullParentName = resolvePreviousParentName(result.getClazz(), unit.getPackageName(), localClassName, parent.getName(), sameThings);
									if (fullParentName != null && !fullParentName.isEmpty()){
										parent.setName(fullParentName);
										newParents.add(parent);
									}
								}
								if (sameThings.size() == 1){
									parent.setName(sameThings.iterator().next());
									newParents.add(parent);
								}
							}
						}
					}
				}
				// задаем новых отфильтрованых родителей
				clazz.getParent().clear();
				clazz.getParent().addAll(newParents);
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
	
	private static String resolvePreviousParentName(List<Class> classes, String packageName, String localClassName, String parentName, Set<String> candidates){
		if (localClassName.lastIndexOf('.') == -1)
			return null;
		String newLocalName = localClassName.substring(0, localClassName.lastIndexOf('.'));
		String searchClass = packageName + '.' + newLocalName;
		for (Class cl : classes)
			if (cl.getName().equals(searchClass))
				for (ParentClass parentCl : cl.getParent()){
					String newParentName = parentName;
					if (parentCl.getName().lastIndexOf('.') > 0)
						newParentName = parentCl.getName().substring(parentCl.getName().lastIndexOf('.')+1, parentCl.getName().length()-1) + '.' + newParentName;
					else
						newParentName = parentCl.getName() + '.' + newParentName;
					Set<String> sameEndings = searchForEnding(candidates, newParentName);
					if (sameEndings.size() > 1)
						return resolvePreviousParentName(classes, packageName, newLocalName, newParentName, sameEndings);
					if (sameEndings.size() == 1)
						return sameEndings.iterator().next();
				}
		return null;
	}

	private static Set<String> searchForEnding(Set<String> strings, String ending){
		Set<String> result = new HashSet<String>();
		for (String str : strings)
			if (str.endsWith(ending))
				result.add(str);
		return result;
	}
}
