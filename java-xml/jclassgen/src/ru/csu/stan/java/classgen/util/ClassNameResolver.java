package ru.csu.stan.java.classgen.util;

import java.math.BigInteger;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import ru.csu.stan.java.classgen.automaton.ClassContext;
import ru.csu.stan.java.classgen.jaxb.AggregatedType;
import ru.csu.stan.java.classgen.jaxb.BaseTypedElement;
import ru.csu.stan.java.classgen.jaxb.Class;
import ru.csu.stan.java.classgen.jaxb.Classes;
import ru.csu.stan.java.classgen.jaxb.CommonType;
import ru.csu.stan.java.classgen.jaxb.ObjectFactory;
import ru.csu.stan.java.classgen.jaxb.ParentClass;

public class ClassNameResolver {

	private ImportRegistry imports;
	private PackageRegistry packages;
	
	private ClassNameResolver(ClassContext context){
		this.imports = context.getImpReg();
		this.packages = context.getPackageReg();
	}
	
	public static ClassNameResolver getInstance(ClassContext context){
		return new ClassNameResolver(context);
	}
	
	/**
	 * Получение полного имени типа.
	 * @param name исходное имя класса (может уже быть полным).
	 * @param currentClass текущий обрабатываемый класс, в котором выполняется поиск полного имени типа.
	 * @param allClasses все классы проекта.
	 * @return полное имя типа, null - если в проекте не описан соответствующий тип.
	 */
	public String getFullTypeName(String name, Class currentClass, Classes allClasses)
	{
		// все по простому: класс нормально импортирован из проекта
		if (packages.isClassInRegistry(name))
			return name;
		// всякие сложности
		else{
			return findFullClassNameInProject(name, currentClass, allClasses);
		}
	}

	/**
	 * Поиск полного типа класса внутри исследуемого проекта.
	 * @param name
	 * @param currentClass
	 * @param allClasses
	 * @return 
	 */
	private String findFullClassNameInProject(String name, Class currentClass, Classes allClasses) {
		// Получаем метаданные о файле сборки
		CompilationUnit unit = imports.findUnitByClass(currentClass.getName());
		
		String currentPackageName = findNameInCurrentPackage(name, unit);
		if (currentPackageName != null)
			return currentPackageName;
		
		String starImportedName = findNameInStarImports(name, unit);
		if (starImportedName != null)
			return starImportedName;
		
		return findNameInContainerClass(name, currentClass, allClasses, unit);
	}

	/**
	 * Получение полного имени из класса, для которого текущий является вложенным.
	 * Если текущий вложенным не является, тогда результат будет null.
	 * @param name
	 * @param currentClass
	 * @param allClasses
	 * @param unit
	 * @return
	 */
	private String findNameInContainerClass(String name, Class currentClass, Classes allClasses, CompilationUnit unit) {
		String localCurrentClassName = currentClass.getName().substring(unit.getPackageName().length()+1);
		if (localCurrentClassName.indexOf('.') > 0){
			Set<String> sameThings = getAllFullNamesWithSameBeginningAndEnding(name, unit);
			if (sameThings.size() > 1){
				String fullTypeName = resolveNameInContainerClassParent(allClasses.getClazz(), unit.getPackageName(), localCurrentClassName, name, sameThings);
				if (fullTypeName != null && !fullTypeName.isEmpty()){
					return fullTypeName;
				}
			}
			if (sameThings.size() == 1){
				return sameThings.iterator().next();
			}
		}
		return null;
	}

	/**
	 * @param name
	 * @param unit
	 * @return
	 */
	private Set<String> getAllFullNamesWithSameBeginningAndEnding(String name, CompilationUnit unit) {
		Set<String> sameThings = new HashSet<String>();
		for (String imp : unit.getImports())
			sameThings.addAll(packages.getClassesByPrefixAndPostfix(imp, name));
		sameThings.addAll(packages.getClassesByPrefixAndPostfix(unit.getPackageName(), name));
		return sameThings;
	}

	/**
	 * @param name
	 * @param unit
	 */
	private String findNameInStarImports(String name, CompilationUnit unit) {
		for (String starImport : unit.getStarImports()){
			// отбрасываем ".*"
			String fullName = packages.findFullNameByShortInPackage(starImport.substring(0, starImport.length()-2), name);
			if (fullName != null){
				return fullName;
			}
		}
		return null;
	}

	/**
	 * Поиск имени в текущем пакете.
	 * @param name
	 * @param unit
	 */
	private String findNameInCurrentPackage(String name, CompilationUnit unit) {
		String fullName = packages.findFullNameByShortInPackage(unit.getPackageName(), name);
		if (fullName != null){
			return fullName;
		}
		return null;
	}

	/**
	 * Поиск в наборе строк тех, что имеют заданное окончание.
	 * @param strings набор строк для поиска.
	 * @param ending окончание, по которому идет поиск.
	 * @return Набор строк, подобранных среди исходного.
	 */
	private Set<String> searchForEnding(Set<String> strings, String ending){
		Set<String> result = new HashSet<String>();
		for (String str : strings)
			if (str.endsWith(ending))
				result.add(str);
		return result;
	}

	/**
	 * Попытка получение полного имени объемлющего класса.
	 * @param classes
	 * @param packageName
	 * @param localClassName
	 * @param name
	 * @param candidates
	 * @return
	 */
	private String resolveNameInContainerClassParent(List<Class> classes, String packageName, String localClassName, String name, Set<String> candidates){
		if (localClassName.lastIndexOf('.') == -1)
			return null;
		String containerClassName = localClassName.substring(0, localClassName.lastIndexOf('.'));
		String searchClass = packageName + '.' + containerClassName;
		for (Class cl : classes)
			if (cl.getName().equals(searchClass))
				for (ParentClass parentCl : cl.getParent()){
					String searchingNameInContainersParent = name;
					if (parentCl.getName().lastIndexOf('.') > 0)
						searchingNameInContainersParent = parentCl.getName().substring(parentCl.getName().lastIndexOf('.')+1, parentCl.getName().length()-1) + '.' + searchingNameInContainersParent;
					else
						searchingNameInContainersParent = parentCl.getName() + '.' + searchingNameInContainersParent;
					Set<String> sameEndings = searchForEnding(candidates, searchingNameInContainersParent);
					if (sameEndings.size() > 1)
						return resolveNameInContainerClassParent(classes, packageName, containerClassName, searchingNameInContainersParent, sameEndings);
					if (sameEndings.size() == 1)
						return sameEndings.iterator().next();
				}
		return null;
	}

	/**
	 * @param element
	 * @param clazz
	 * @param allClasses
	 * @param objectFactory
	 */
	public void resolveTypeNames(BaseTypedElement element, Class clazz, Classes allClasses, ObjectFactory objectFactory) {
		List<CommonType> type = element.getCommonType();
		if (type != null && type.size() > 0){
			String fullTypeName = getFullTypeName(type.get(0).getName(), clazz, allClasses);
			if (fullTypeName != null && !fullTypeName.isEmpty()){
				type.get(0).setName(fullTypeName);
			}
			else
				element.getCommonType().clear();
		}
		List<AggregatedType> aType = element.getAggregatedType();
		if (aType != null && aType.size() > 0){
			String fullTypeName = getFullTypeName(aType.get(0).getName(), clazz, allClasses);
			String fullAgregatedTypeName = getFullTypeName(aType.get(0).getElementType(), clazz, allClasses);
			if (fullTypeName != null && !fullTypeName.isEmpty()){
				element.getAggregatedType().clear();
				CommonType newType = objectFactory.createCommonType();
				newType.setName(fullTypeName);
				element.getCommonType().add(newType);
			}
			else
				if (fullAgregatedTypeName != null && !fullAgregatedTypeName.isEmpty())
				{
					aType.get(0).setElementType(fullAgregatedTypeName);
					aType.get(0).setId(BigInteger.valueOf(-1));
				}
				else
					element.getAggregatedType().clear();
		}
	}

}
