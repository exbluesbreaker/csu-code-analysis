package ru.csu.stan.java.classgen.main;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;
import javax.xml.stream.XMLEventReader;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.events.XMLEvent;

import ru.csu.stan.java.classgen.handlers.HandlerFactory;
import ru.csu.stan.java.classgen.handlers.IStaxHandler;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.jaxb.ObjectFactory;
import ru.csu.stan.java.classgen.util.ClassContext;

/**
 * Генератор универсального классового представления
 * по AST-представлению Java-кода.
 * Точка входа.
 * 
 * @author mz
 *
 */
public class Main {

	private static String[] input = {"../test/src/com/example/MyClass.java.stax.xml",};
//		"../test/src/java/lang/LinkedList.java.stax.xml"};
	
	/**
	 * Точка входа
	 * @param args
	 */
	public static void main(String[] args) {
		ObjectFactory factory = new ObjectFactory();
		Classes result = factory.createClasses();
		HandlerFactory handlers = HandlerFactory.getInstance();
		XMLInputFactory xmlFactory = XMLInputFactory.newInstance();
		try{
			for (String filename : input){
				File f = new File(filename);
				XMLEventReader reader = xmlFactory.createXMLEventReader(new FileInputStream(f));
				ClassContext context = ClassContext.getInstance(result, factory);
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
		}
		catch (FileNotFoundException e) {
			System.out.println("File not found!");
			e.printStackTrace();
		}
		catch (XMLStreamException e) {
			System.out.println("Wrong XML");
			e.printStackTrace();
		}
		try {
			JAXBContext context = JAXBContext.newInstance("ru.csu.stan.java.classgen.jaxb");
			Marshaller marshaller = context.createMarshaller();
			marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true);
			marshaller.marshal(result, new File("resources/classes.xml"));
		} 
		catch (JAXBException e) {
			e.printStackTrace();
		}
		
	}

}
