package ru.csu.stan.java.classgen.main;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.math.BigInteger;
import java.util.LinkedList;
import java.util.List;

import javax.xml.stream.FactoryConfigurationError;
import javax.xml.stream.XMLEventReader;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.events.XMLEvent;

import ru.csu.stan.java.classgen.automaton.ClassContext;
import ru.csu.stan.java.classgen.automaton.IContext;
import ru.csu.stan.java.classgen.handlers.HandlerFactory;
import ru.csu.stan.java.classgen.handlers.IStaxHandler;
import ru.csu.stan.java.classgen.jaxb.AggregatedType;
import ru.csu.stan.java.classgen.jaxb.Argument;
import ru.csu.stan.java.classgen.jaxb.Attribute;
import ru.csu.stan.java.classgen.jaxb.BaseTypedElement;
import ru.csu.stan.java.classgen.jaxb.Class;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.jaxb.CommonType;
import ru.csu.stan.java.classgen.jaxb.Method;
import ru.csu.stan.java.classgen.jaxb.ObjectFactory;
import ru.csu.stan.java.classgen.jaxb.ParentClass;
import ru.csu.stan.java.classgen.util.ClassIdGenerator;
import ru.csu.stan.java.classgen.util.ClassNameResolver;

/**
 * Генератор универсального классового представления.
 * Строит представление в 3 прохода:
 * <ol>
 * <li>1 - Строится основное дерево классов, считывается пакетная структура и структура импортов</li>
 * <li>2 - На основе пакетной структуры получаются полные имена классов, системные и библиотечные классы отбрасываются</li>
 * <li>3 - Для полных имен генерируются и устанавливаются ID</li>
 * </ol>
 * 
 * @author mz
 *
 */
public class UCRGenerator {

	private ObjectFactory objectFactory;
	private HandlerFactory handlersFactory;
	private XMLInputFactory xmlFactory;
	
	private UCRGenerator() {
		objectFactory = new ObjectFactory();
		handlersFactory = HandlerFactory.getInstance();
		xmlFactory = XMLInputFactory.newInstance();
	}
	
	public static UCRGenerator createInstance() {
		return new UCRGenerator();
	}

	/**
	 * @param input
	 * @return
	 * @throws FactoryConfigurationError
	 */
	public Classes processInputFile(final String input) throws FactoryConfigurationError {
		Classes result = objectFactory.createClasses();
		IContext<Classes> context = ClassContext.getInstance(result, objectFactory);
		context = firstPass(input, context);
		secondPass(result, context);
		thirdPass(result);
		return result;
	}

	/**
	 * Третий проход, расстановка ID
	 * @param result
	 */
	private void thirdPass(Classes result) {
		System.out.println("Generating IDs for classes");
		for (Class clazz : result.getClazz()){
			for (ParentClass parent : clazz.getParent())
				parent.setId(ClassIdGenerator.getInstance().getClassId(parent.getName()));
			for (Attribute attr: clazz.getAttr()){
				generateIdForTypes(attr);
			}
			for (Method method: clazz.getMethod()){
				generateIdForTypes(method);
				for (Argument arg: method.getArg()){
					generateIdForTypes(arg);
				}
			}
		}
	}

	/**
	 * @param typedElement
	 */
	private void generateIdForTypes(BaseTypedElement typedElement) {
		if (typedElement.getCommonType().size() > 0)
			typedElement.getCommonType().get(0).setId(ClassIdGenerator.getInstance().getClassId(typedElement.getCommonType().get(0).getName()));
		if (typedElement.getAggregatedType().size() > 0){
			if (typedElement.getAggregatedType().get(0).getId()!= null && typedElement.getAggregatedType().get(0).getId().intValue() != -1)
				typedElement.getAggregatedType().get(0).setId(ClassIdGenerator.getInstance().getClassId(typedElement.getAggregatedType().get(0).getName()));
			typedElement.getAggregatedType().get(0).setElementId(ClassIdGenerator.getInstance().getClassId(typedElement.getAggregatedType().get(0).getElementType()));
		}
	}

	/**
	 * Второй проход, установление связей между типами и родительскими классами
	 * 
	 * @param result
	 * @param context
	 */
	private void secondPass(Classes result, IContext<Classes> context) {
		System.out.println("Resolving parent classes");
		ClassNameResolver nameResolver = ClassNameResolver.getInstance((ClassContext) context);
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
					resolveTypeNames(attr, clazz, result, nameResolver);
				}
			// формируем полные типы для возвращаемых значений из методов
			if (clazz.getMethod() != null)
				for (Method method: clazz.getMethod()){
					resolveTypeNames(method, clazz, result, nameResolver);
					
					// формируем полные типы аргументов методов
					if (method.getArg() != null)
						for (Argument arg: method.getArg()){
							resolveTypeNames(arg, clazz, result, nameResolver);
						}
				}
		}
	}

	/**
	 * @param element
	 * @param clazz
	 * @param allClasses
	 * @param nameResolver
	 */
	private void resolveTypeNames(BaseTypedElement element, Class clazz, Classes allClasses, ClassNameResolver nameResolver) {
		List<CommonType> type = element.getCommonType();
		if (type != null && type.size() > 0){
			String fullTypeName = nameResolver.getFullTypeName(type.get(0).getName(), clazz, allClasses);
			if (fullTypeName != null && !fullTypeName.isEmpty()){
				type.get(0).setName(fullTypeName);
			}
			else
				element.getCommonType().clear();
		}
		List<AggregatedType> aType = element.getAggregatedType();
		if (aType != null && aType.size() > 0){
			String fullTypeName = nameResolver.getFullTypeName(aType.get(0).getName(), clazz, allClasses);
			String fullAgregatedTypeName = nameResolver.getFullTypeName(aType.get(0).getElementType(), clazz, allClasses);
			if (fullTypeName != null && !fullTypeName.isEmpty()){
				element.getAggregatedType().clear();
				CommonType newType = objectFactory.createCommonType();
				newType.setName(fullTypeName);
				element.getCommonType().add(newType);
			}
			else
				if (fullAgregatedTypeName != null && !fullAgregatedTypeName.isEmpty())
				{
					aType.get(0).setElementType(fullAgregatedTypeName);
					aType.get(0).setId(BigInteger.valueOf(-1));
				}
				else
					element.getAggregatedType().clear();
		}
	}

	/**
	 * Первый проход обработчика и формирование основного списка классов,
	 * формирование реестра типов
	 * @param input
	 * @param context
	 * @return
	 */
	private IContext<Classes> firstPass(final String input, IContext<Classes> context) {
		
		try{
			File f = new File(input);
			XMLEventReader reader = xmlFactory.createXMLEventReader(new FileInputStream(f));
			try{
				while (reader.hasNext()){
					XMLEvent nextEvent = reader.nextEvent();
					IStaxHandler<Classes> handler = handlersFactory.createHandler(nextEvent);
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

}
