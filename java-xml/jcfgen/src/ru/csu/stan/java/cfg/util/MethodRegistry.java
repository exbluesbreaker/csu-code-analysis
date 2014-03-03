package ru.csu.stan.java.cfg.util;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * 
 * @author mz
 *
 */
public class MethodRegistry {
	
	private Map<String, Set<MethodRegistryItem>> registry = new HashMap<String, Set<MethodRegistryItem>>();
	
	private MethodRegistry() {}
	
	public static MethodRegistry getInstance(){
		return new MethodRegistry();
	}
	
	public void addMethodToRegistry(String className, MethodRegistryItem method){
		if (!registry.containsKey(className))
			registry.put(className, new HashSet<MethodRegistryItem>());
		registry.get(className).add(method);
	}

	public MethodRegistryItem getItem(String className, int id){
		if (registry.containsKey(className))
			for (MethodRegistryItem item: registry.get(className))
				if (item.getId() == id)
					return item;
		return null;
	}
	
	public MethodRegistryItem findSame(String className, MethodRegistryItem query){
		if (registry.containsKey(className))
			for (MethodRegistryItem item: registry.get(className)){
				boolean same = true;
				for (String my: item.getArgs())
					same = same && query.getArgs().contains(my);
				for (String theirs: query.getArgs())
					same = same && item.getArgs().contains(theirs);
				if (item.getName().equals(query.getName()) && same)
					return item;
			}
		return null;
	}
}
