package ru.csu.stan.java.classgen.util;

import java.util.HashSet;
import java.util.Set;

/**
 * Сводный реестр по импортам.
 * Содержит в себе список компилируемых файлов.
 * 
 * @author mz
 *
 */
public class ImportRegistry {

	/** Набор компилируемых файлов */
	private Set<CompilationUnit> units = new HashSet<CompilationUnit>();
	
	/**
	 * Добавление компилируемого файла в реестр.
	 * @param unit
	 */
	public void addCompilationUnit(CompilationUnit unit){
		units.add(unit);
	}
	
	/**
	 * Поиск необходимого компилируемого файла по имени класса.
	 * Ищется файл, в котором класс описан.
	 * @param className
	 * @return
	 */
	public CompilationUnit findUnitByClass(String className){
		for (CompilationUnit unit : units)
			if (unit.hasClass(className))
				return unit;
		return null;
	}
}
