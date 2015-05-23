package ru.csu.stan.java.classgen.main;

import java.io.File;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;

import ru.csu.stan.java.classgen.jaxb.Classes;

/**
 * Генератор универсального классового представления
 * по AST-представлению Java-кода.
 * Точка входа.
 * 
 * @author mz
 *
 */
public class Main {
	
	private static final String HELP = "USAGE: ucr <input file> <output file>";
	
	/**
	 * Точка входа
	 * @param args
	 */
	public static void main(String[] args) {
		if (args != null && args.length > 0 && args.length < 3){
			final String input = args[0];
			final String output = args[1];
			System.out.println("Start working with " + input + " as input file");
			Classes result = UCRGenerator.createInstance().processInputFile(input);
			
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
