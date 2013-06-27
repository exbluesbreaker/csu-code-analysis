package ru.csu.stan.java.cfg.util;

import ru.csu.stan.java.classgen.jaxb.Class;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.util.ClassIdGenerator;
import ru.csu.stan.java.classgen.util.IClassIdGenerator;

/**
 * 
 * @author mz
 *
 */
public class ImportedClassIdGenerator extends ClassIdGenerator {

	private static final ImportedClassIdGenerator instance = new ImportedClassIdGenerator();
	
	protected ImportedClassIdGenerator() {}
	
	public static IClassIdGenerator getInstance(){
		return instance;
	}
	
	public static IClassIdGenerator getInstanceImportClasses(Classes classes){
		instance.importClasses(classes);
		return instance;
	}

	protected void importClasses(Classes classes){
		for (Class clazz: classes.getClazz()){
			setClassId(clazz.getName(), clazz.getId());
		}
	}
}
