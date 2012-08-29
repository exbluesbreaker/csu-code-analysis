package ru.csu.stan.java.classgen.util;

import java.util.HashSet;
import java.util.Set;

public class CompilationUnit {

	private Set<String> imports = new HashSet<String>();
	private Set<String> classes = new HashSet<String>();
	
	public void addImport(String importName){
		imports.add(importName);
	}
	
	public void addClass(String className){
		classes.add(className);
	}
	
	public Set<String> getStarImports(){
		Set<String> result = new HashSet<String>();
		for (String importName : imports)
			if (importName.indexOf('*') > 0)
				result.add(importName);
		return result;
	}
	
	public Set<String> getClasses(){
		return classes;
	}
	
	public boolean hasClass(String className){
		return classes.contains(className);
	}
}
