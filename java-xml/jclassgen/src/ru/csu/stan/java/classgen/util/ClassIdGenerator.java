package ru.csu.stan.java.classgen.util;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.Map;

/**
 * Фабрика генерации идентификаторов для классов.
 * 
 * @author mz
 *
 */
public class ClassIdGenerator implements IClassIdGenerator {

	/** Единственный экхемпляр, для обеспечения уникальности */
	private static final IClassIdGenerator instance = new ClassIdGenerator();
	
	/** Словарь полных имен классов и ID, поставленных им в соответствие */
	private Map<String, BigInteger> ids = new HashMap<String, BigInteger>();
	
	/** Следующий доступный ID класса */
	private int id = 1;
	
	/** 
	 * Закрытый конструктор.
	 * @see #getInstance()
	 */
	protected ClassIdGenerator() {}
	
	/**
	 * Получение экземпляра фабрики.
	 * Гарантировано, что экземпляр будет всегда одинаковый.
	 * @return
	 */
	public static IClassIdGenerator getInstance(){
		return instance;
	}

	@Override
	public BigInteger getClassId(String className){
		if (!isClassWithId(className))
			setClassId(className, getNextId());
		return getClassIdNotSafe(className);
	}

	/**
	 * @return
	 */
	protected BigInteger getNextId() {
		return BigInteger.valueOf(id++);
	}

	/**
	 * @param className
	 * @return
	 */
	protected BigInteger getClassIdNotSafe(String className) {
		return ids.get(className);
	}

	/**
	 * @param className
	 * @param id
	 */
	protected void setClassId(String className, BigInteger id) {
		ids.put(className, id);
	}

	/**
	 * @param className
	 * @return
	 */
	protected boolean isClassWithId(String className) {
		return ids.containsKey(className);
	}
}
