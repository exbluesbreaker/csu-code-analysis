package ru.csu.stan.ui.main;

import java.io.File;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Unmarshaller;

import ru.csu.stan.java.classgen.jaxb.Argument;
import ru.csu.stan.java.classgen.jaxb.Attribute;
import ru.csu.stan.java.classgen.jaxb.Class;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.jaxb.Method;
import ru.csu.stan.ui.code.Project;

public class Main {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		if (args.length == 1)
			try {
				JAXBContext jcontext = JAXBContext.newInstance("ru.csu.stan.java.classgen.jaxb");
				Unmarshaller unmarshaller = jcontext.createUnmarshaller();
				File file = new File(args[0]);
				Classes classes = (Classes) unmarshaller.unmarshal(file);
				Project project = Project.createInstance();
				for (Class clazz: classes.getClazz()){
					project.addAnchor(clazz.getFilename(), clazz);
					for (Attribute attribute: clazz.getAttr())
						project.addAnchor(clazz.getFilename(), attribute);
					for (Method method: clazz.getMethod()){
						project.addAnchor(clazz.getFilename(), method);
						for (Argument argument: method.getArg())
							project.addAnchor(clazz.getFilename(), argument);
					}
				}
			} 
			catch (JAXBException e) {
				e.printStackTrace();
			}
		else{
			System.out.println("Usage: Main <filename>");
			System.exit(1);
		}
	}
	
}
