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
import ru.csu.stan.java.classgen.jaxb.Attribute;
import ru.csu.stan.java.classgen.jaxb.Class;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.jaxb.CommonType;
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
			// Первый проход обработчика и формирование основного списка классов,
			// формирование реестра типов
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
			// Второй проход, установление связей между типами и родительскими классами
			System.out.println("Resolving parent classes");
			ImportRegistry imports = context.getImpReg();
			PackageRegistry packages = context.getPackageReg();
			for (Class clazz : result.getClazz()){
				// формируем новый список родителей
				List<ParentClass> newParents = new LinkedList<ParentClass>();
				for (ParentClass parent : clazz.getParent()){
					String fullParentName = getFullTypeName(packages, imports, parent.getName(), clazz, result);
					if (fullParentName != null && !fullParentName.isEmpty())
					{
						parent.setName(fullParentName);
						newParents.add(parent);
					}
				}
				// задаем новых отфильтрованых родителей
				clazz.getParent().clear();
				clazz.getParent().addAll(newParents);
				// формируем полные типы для полей
				if (clazz.getAttr() != null)
					for (Attribute attr: clazz.getAttr()){
						List<CommonType> type = attr.getCommonType();
						if (type != null && type.size() > 0){
							String fullTypeName = getFullTypeName(packages, imports, type.get(0).getName(), clazz, result);
							if (fullTypeName != null && !fullTypeName.isEmpty())
							{
								type.get(0).setName(fullTypeName);
							}
							else
								attr.getCommonType().clear();
						}
					}
			}
			
			System.out.println("Generating IDs for classes");
			for (Class clazz : result.getClazz()){
				if (clazz.getParent() != null)
					for (ParentClass parent : clazz.getParent())
						parent.setId(ClassIdGenerator.getInstance().getClassId(parent.getName()));
				if (clazz.getAttr() != null)
					for (Attribute attr: clazz.getAttr())
						if (attr.getCommonType().size() > 0)
							attr.getCommonType().get(0).setId(ClassIdGenerator.getInstance().getClassId(attr.getCommonType().get(0).getName()));
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
	
	/**
	 * Получение полного имени типа.
	 * @param name
	 * @return полное имя типа, null - если в проекте не описан соответствующий тип.
	 */
	private static String getFullTypeName(PackageRegistry packages, ImportRegistry imports, String name, Class clazz, Classes result)
	{
		// все по простому: родитель нормально импортирован из проекта
		if (packages.isClassInRegistry(name))
			return name;
		// всякие сложности
		else{
			CompilationUnit unit = imports.findUnitByClass(clazz.getName());
			for (String starImport : unit.getStarImports()){
				// отбрасываем ".*"
				String fullName = packages.findFullNameByShortInPackage(starImport.substring(0, starImport.length()-2), name);
				if (fullName != null){
					return fullName;
				}
			}
			String fullName = packages.findFullNameByShortInPackage(unit.getPackageName(), name);
			if (fullName != null){
				return fullName;
			}
			String localClassName = clazz.getName().substring(unit.getPackageName().length()+1);
			if (localClassName.indexOf('.') > 0){
				Set<String> sameThings = new HashSet<String>();
				for (String imp : unit.getImports())
					sameThings.addAll(packages.getClassesByPrefixAndPostfix(imp, name));
				if (sameThings.size() > 1){
					String fullTypeName = resolvePreviousParentName(result.getClazz(), unit.getPackageName(), localClassName, name, sameThings);
					if (fullTypeName != null && !fullTypeName.isEmpty()){
						return fullTypeName;
					}
				}
				if (sameThings.size() == 1){
					return sameThings.iterator().next();
				}
			}
		}
		return null;
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

	/**
	 * Поиск в наборе строк тех, что имеют заданное окончание.
	 * @param strings набор строк для поиска.
	 * @param ending окончание, по которому идет поиск.
	 * @return Набор строк, подобранных среди исходного.
	 */
	private static Set<String> searchForEnding(Set<String> strings, String ending){
		Set<String> result = new HashSet<String>();
		for (String str : strings)
			if (str.endsWith(ending))
				result.add(str);
		return result;
	}
}
