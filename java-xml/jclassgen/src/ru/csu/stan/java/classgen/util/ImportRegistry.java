package ru.csu.stan.java.classgen.util;

import java.util.HashSet;
import java.util.Set;

public class ImportRegistry {

	private Set<CompilationUnit> units = new HashSet<CompilationUnit>();
	
	public void addCompilationUni(CompilationUnit unit){
		units.add(unit);
	}
	
	public CompilationUnit findUnitByClass(String className){
		for (CompilationUnit unit : units)
			if (unit.hasClass(className))
				return unit;
		return null;
	}
}
