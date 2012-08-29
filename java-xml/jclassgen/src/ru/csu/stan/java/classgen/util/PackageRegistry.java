package ru.csu.stan.java.classgen.util;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

public class PackageRegistry{

	private Map<String, Set<String>> internal = new HashMap<String, Set<String>>();
	private Set<String> allClasses = new HashSet<String>();
	
	public Set<String> getPackageClasses(String packageName){
		Set<String> result = new HashSet<String>();
		for (Entry<String, Set<String>> internalEntry : internal.entrySet())
			if (internalEntry.getKey().indexOf(packageName) > 0)
				result.addAll(internalEntry.getValue());
		return result;
	}

	public boolean addClassToPackage(String className, String packageName){
		if (!internal.containsKey(packageName))
			internal.put(packageName, new HashSet<String>());
		return internal.get(packageName).add(className);
	}
	
	public boolean existPackage(String packageName){
		for (String name : internal.keySet())
			if (name.indexOf(packageName) > 0)
				return true;
		return false;
	}
	
	public boolean isClassInRegistry(String className){
		return false;
	}
}
