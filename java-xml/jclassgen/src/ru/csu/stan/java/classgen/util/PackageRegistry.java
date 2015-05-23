package ru.csu.stan.java.classgen.util;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

/**
 * Реестр всех пакетов проекта и всех классов, описанных в них.
 * 
 * @author mz
 *
 */
public class PackageRegistry{

	/** Словарь соответствия имени пакета и набора классов, в нем описанных. */
	private Map<String, Set<String>> internal = new HashMap<String, Set<String>>();
	
	/** Набор, содержащий абсолютно все классы проекта. Хранит полные имена классов */
	private Set<String> allClasses = new HashSet<String>();
	
	/**
	 * Получение словаря пакетов и классов в них по указанному пакету.
	 * Ищет вложенные пакеты, за счет чего и получается множественный результат.
	 * @param packageName
	 * @return
	 */
	public Map<String, Set<String>> getPackageClasses(String packageName){
		Map<String, Set<String>> result = new HashMap<String, Set<String>>();
		for (Entry<String, Set<String>> internalEntry : internal.entrySet())
			if (internalEntry.getKey().startsWith(packageName))
				result.put(internalEntry.getKey(), internalEntry.getValue());
		return result;
	}

	/**
	 * Добавление класса в пакете в реестр.
	 * @param className короткое имя класса (в файле).
	 * @param packageName имя пакета.
	 * @return
	 */
	public boolean addClassToPackage(String className, String packageName){
		if (!internal.containsKey(packageName))
			internal.put(packageName, new HashSet<String>());
		allClasses.add(packageName + '.' + className);
		return internal.get(packageName).add(className);
	}
	
	/**
	 * Проверка на то, что указанный пакет существует в реестре.
	 * @param packageName
	 * @return
	 */
	public boolean existPackage(String packageName){
		for (String name : internal.keySet())
			if (name.indexOf(packageName) > 0)
				return true;
		return false;
	}
	
	/**
	 * Проверка на наличие класса в реестре по полному имени.
	 * @param className
	 * @return
	 */
	public boolean isClassInRegistry(String className){
		return allClasses.contains(className);
	}
	
	/**
	 * Получение списка полных имен классов по префиксу и постфиксу.
	 * Префикс может быть задан в формате пакетного импорта, 
	 * то есть как "импорт со звездочкой" com.example.* .
	 * @param prefix префикс полного имени класса.
	 * @param postfix постфикс полного имени класса.
	 * @return набор полных имен классов.
	 */
	public Set<String> getClassesByPrefixAndPostfix(String prefix, String postfix){
		Set<String> result = new HashSet<String>();
		String newPrefix;
		if (prefix.lastIndexOf(".*") > 0)
			newPrefix = prefix.substring(0, prefix.lastIndexOf(".*"));
		else
			newPrefix = prefix;
		for (String className : allClasses)
			if (className.startsWith(newPrefix) && className.endsWith(postfix))
				result.add(className);
		return result;
	}

	/**
	 * Поиск класса в указанном пакете по короткому имени.
	 * Возвращается полное имя класса из указанного пакета, если таковой был найден.
	 * @param packageName имя пакета для поиска.
	 * @param localName имя искомого класса.
	 * @return полное пакетное имя класса, если он был найден, иначе - null.
	 */
	public String findFullNameByShortInPackage(String packageName, String localName){
		Map<String, Set<String>> classesFromStarPackage = this.getPackageClasses(packageName);
		for (Entry<String, Set<String>> pkg: classesFromStarPackage.entrySet())
			for (String cl : pkg.getValue())
				if (cl.equals(localName)){
					return pkg.getKey() + '.' + cl;
				}
		return null;
	}
}
