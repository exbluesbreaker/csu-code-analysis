package ru.csu.stan.java.classgen.util;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

public class PackageRegistry{

	private Map<String, Set<String>> internal = new HashMap<String, Set<String>>();
	private Set<String> allClasses = new HashSet<String>();
	
	public Map<String, Set<String>> getPackageClasses(String packageName){
		Map<String, Set<String>> result = new HashMap<String, Set<String>>();
		for (Entry<String, Set<String>> internalEntry : internal.entrySet())
			if (internalEntry.getKey().startsWith(packageName))
				result.put(internalEntry.getKey(), internalEntry.getValue());
		return result;
	}

	public boolean addClassToPackage(String className, String packageName){
		if (!internal.containsKey(packageName))
			internal.put(packageName, new HashSet<String>());
		allClasses.add(packageName + '.' + className);
		return internal.get(packageName).add(className);
	}
	
	public boolean existPackage(String packageName){
		for (String name : internal.keySet())
			if (name.indexOf(packageName) > 0)
				return true;
		return false;
	}
	
	public boolean isClassInRegistry(String className){
		return allClasses.contains(className);
	}
	
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
}
