package ru.csu.stan.java.classgen.util;

import java.math.BigInteger;

public interface IClassIdGenerator {

	/**
	 * Получение ID класса по его полному имени.
	 * Если классу не назначен ID, то он будет сгенерирован,
	 * иначе возвратится уже назначенный.
	 * @param className
	 * @return
	 */
	public abstract BigInteger getClassId(String className);

}