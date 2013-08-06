package ru.csu.stan.ui.main;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;

import javax.annotation.processing.FilerException;
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
		if (args.length == 3)
			try {
				System.out.println("Started");
				JAXBContext jcontext = JAXBContext.newInstance("ru.csu.stan.java.classgen.jaxb");
				Unmarshaller unmarshaller = jcontext.createUnmarshaller();
				File file = new File(args[0]);
				Classes classes = (Classes) unmarshaller.unmarshal(file);
				Project project = Project.createInstance();
				for (Class clazz: classes.getClazz()){
					project.addAnchor(clazz.getFilename(), clazz, String.valueOf(clazz.getId()));
					int aIndex = 0, mIndex = 0;
					for (Attribute attribute: clazz.getAttr())
						project.addAnchor(clazz.getFilename(), attribute, String.valueOf(clazz.getId()) + "." + String.valueOf(aIndex++));
					for (Method method: clazz.getMethod()){
						project.addAnchor(clazz.getFilename(), method, String.valueOf(clazz.getId()) + "." + String.valueOf(mIndex));
						int arIndex = 0;
						for (Argument argument: method.getArg())
							project.addAnchor(clazz.getFilename(), argument, String.valueOf(clazz.getId()) + "." + String.valueOf(mIndex) + "." + String.valueOf(arIndex++));
						mIndex++;
					}
				}
				project.processFiles(args[1], args[2]);
			} 
			catch (JAXBException e) {
				e.printStackTrace();
			} catch (FileNotFoundException e) {
				e.printStackTrace();
			} catch (FilerException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}
		else{
			System.out.println("Usage: Main <ucr-filename> <source-root-dir> <output-root-dir>");
			System.exit(1);
		}
	}
	
}
