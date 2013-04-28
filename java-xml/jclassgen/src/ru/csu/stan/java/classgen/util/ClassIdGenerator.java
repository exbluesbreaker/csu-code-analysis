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
public class ClassIdGenerator {

	/** Единственный экхемпляр, для обеспечения уникальности */
	private static final ClassIdGenerator instance = new ClassIdGenerator();
	
	/** Словарь полных имен классов и ID, поставленных им в соответствие */
	private Map<String, BigInteger> ids = new HashMap<String, BigInteger>();
	
	/** Следующий доступный ID класса */
	private int id = 1;
	
	/** 
	 * Закрытый конструктор.
	 * @see #getInstance()
	 */
	private ClassIdGenerator() {}
	
	/**
	 * Получение экземпляра фабрики.
	 * Гарантировано, что экземпляр будет всегда одинаковый.
	 * @return
	 */
	public static ClassIdGenerator getInstance(){
		return instance;
	}
	
	/**
	 * Получение ID класса по его полному имени.
	 * Если классу не назначен ID, то он будет сгенерирован,
	 * иначе возвратится уже назначенный.
	 * @param className
	 * @return
	 */
	public BigInteger getClassId(String className){
		if (!ids.containsKey(className))
			ids.put(className, BigInteger.valueOf(id++));
		return ids.get(className);
	}
}
