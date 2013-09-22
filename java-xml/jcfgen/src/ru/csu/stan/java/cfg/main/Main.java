package ru.csu.stan.java.cfg.main;

import java.io.File;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;

import ru.csu.stan.java.cfg.jaxb.Project;

/**
 * 
 * @author mz
 *
 */
public class Main {
	
	private static final String HELP = "USAGE: cfg <output file> <input AST> <input UCR(optional)>\n" +
			"You can specify UCR to import class IDs from it. Without UCR IDs will be generated automatically.";

	/**
	 * Точка входа
	 * @param args
	 */
	public static void main(String[] args) {
		if (args!= null && (args.length == 2 || args.length == 3)){
			final String output = args[0];
			final String inputAst = args[1];
			System.out.println("Start working with " + inputAst + " as input file");
			final String inputUcr;
			if (args.length == 3){
				inputUcr = args[2];
				System.out.println("Using UCR " + inputUcr + " for class IDs");
			}
			else
				inputUcr = null;
			CFGGenerator generator = CFGGenerator.getInstance();
			try {
				generator.importUcrIds(inputUcr);
			} catch (JAXBException e) {
				e.printStackTrace();
				System.exit(1);
			}
			Project result = generator.processInputFile(inputAst);
			try {
				JAXBContext jcontext = JAXBContext.newInstance("ru.csu.stan.java.cfg.jaxb");
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
