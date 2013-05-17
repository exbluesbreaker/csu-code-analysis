package ru.csu.stan.java.classgen.main;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.LinkedList;
import java.util.List;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;
import javax.xml.stream.XMLEventReader;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.events.XMLEvent;

import ru.csu.stan.java.classgen.automaton.ClassContext;
import ru.csu.stan.java.classgen.handlers.HandlerFactory;
import ru.csu.stan.java.classgen.handlers.IStaxHandler;
import ru.csu.stan.java.classgen.jaxb.Argument;
import ru.csu.stan.java.classgen.jaxb.Attribute;
import ru.csu.stan.java.classgen.jaxb.Class;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.jaxb.CommonType;
import ru.csu.stan.java.classgen.jaxb.Method;
import ru.csu.stan.java.classgen.jaxb.ObjectFactory;
import ru.csu.stan.java.classgen.jaxb.ParentClass;
import ru.csu.stan.java.classgen.jaxb.Type;
import ru.csu.stan.java.classgen.util.ClassIdGenerator;
import ru.csu.stan.java.classgen.util.ClassNameResolver;

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
			ClassNameResolver nameResolver = ClassNameResolver.getInstance(context);
			for (Class clazz : result.getClazz()){
				// формируем новый список родителей
				List<ParentClass> newParents = new LinkedList<ParentClass>();
				for (ParentClass parent : clazz.getParent()){
					String fullParentName = nameResolver.getFullTypeName(parent.getName(), clazz, result);
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
							String fullTypeName = nameResolver.getFullTypeName(type.get(0).getName(), clazz, result);
							if (fullTypeName != null && !fullTypeName.isEmpty())
							{
								type.get(0).setName(fullTypeName);
							}
							else
								attr.getCommonType().clear();
						}
					}
				// формируем полные типы для возвращаемых значений из методов
				if (clazz.getMethod() != null)
					for (Method method: clazz.getMethod()){
						List<Type> type = method.getType();
						if (type != null && type.size() > 0){
							String fullTypeName = nameResolver.getFullTypeName(type.get(0).getName(), clazz, result);
							if (fullTypeName != null && !fullTypeName.isEmpty())
							{
								type.get(0).setName(fullTypeName);
							}
							else
								method.getType().clear();
						}
						// формируем полные типы аргументов методов
						if (method.getArg() != null)
							for (Argument arg: method.getArg()){
								List<Type> argumentType = arg.getType();
								if (argumentType != null && argumentType.size() > 0){
									String fullTypeName = nameResolver.getFullTypeName(argumentType.get(0).getName(), clazz, result);
									if (fullTypeName != null && !fullTypeName.isEmpty())
									{
										argumentType.get(0).setName(fullTypeName);
									}
									else
										arg.getType().clear();
								}
							}
					}
			}
			
			System.out.println("Generating IDs for classes");
			for (Class clazz : result.getClazz()){
				for (ParentClass parent : clazz.getParent())
					parent.setId(ClassIdGenerator.getInstance().getClassId(parent.getName()));
				for (Attribute attr: clazz.getAttr())
					if (attr.getCommonType().size() > 0)
						attr.getCommonType().get(0).setId(ClassIdGenerator.getInstance().getClassId(attr.getCommonType().get(0).getName()));
				for (Method method: clazz.getMethod()){
					if (method.getType().size() > 0)
						method.getType().get(0).setId(ClassIdGenerator.getInstance().getClassId(method.getType().get(0).getName()));
					for (Argument arg: method.getArg())
						if (arg.getType().size() > 0)
							arg.getType().get(0).setId(ClassIdGenerator.getInstance().getClassId(arg.getType().get(0).getName()));
				}
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
