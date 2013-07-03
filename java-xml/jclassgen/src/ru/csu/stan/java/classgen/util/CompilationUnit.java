package ru.csu.stan.java.classgen.util;

import java.util.HashSet;
import java.util.Set;

/**
 * Компилируемый файл с точки зрения хранимых в нем типов.
 * Необходим для хранения импортов.
 * 
 * @author mz
 *
 */
public class CompilationUnit {

	/** Импорты в файле */
	private Set<String> imports = new HashSet<String>();
	
	/** Имена классов в файле */
	private Set<String> classes = new HashSet<String>();
	
	/** Имя пакета в файле */
	private String packageName;
	
	/** Имя файла */
	private String filename;
	
	/**
	 * Получение имени текущего файла.
	 * @return
	 */
	public String getFilename() {
		return filename;
	}

	/**
	 * Установка значения имени текущего файла.
	 * @param filename
	 */
	public void setFilename(String filename) {
		this.filename = filename;
	}

	/**
	 * Получение имени пакета в текущем файле.
	 * @return
	 */
	public String getPackageName() {
		return packageName;
	}

	/**
	 * Установка имени пакета в текущем файле.
	 * @param packageName
	 */
	public void setPackageName(String packageName) {
		this.packageName = packageName;
	}

	/**
	 * Добавление в файл импорта.
	 * @param importName
	 */
	public void addImport(String importName){
		imports.add(importName);
	}
	
	/**
	 * Добавление в файл имени класса, описанного там.
	 * @param className
	 */
	public void addClass(String className){
		classes.add(className);
	}
	
	/**
	 * Получение всех "импортов со звездочкой", то есть, импортов пакета целиком.
	 * @return
	 */
	public Set<String> getStarImports(){
		Set<String> result = new HashSet<String>();
		for (String importName : imports)
			if (importName.indexOf('*') > 0)
				result.add(importName);
		return result;
	}
	
	/**
	 * Получение списка классов, определенных в файле.
	 * @return
	 */
	public Set<String> getClasses(){
		return classes;
	}
	
	/**
	 * Проверка на то, что в файле имеется указанный класс.
	 * @param className
	 * @return
	 */
	public boolean hasClass(String className){
		return classes.contains(className);
	}
	
	/**
	 * Получение списка импортов в файле.
	 * @return
	 */
	public Set<String> getImports(){
		return imports;
	}
}
