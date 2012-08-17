package ru.csu.stan.java.classgen.util;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.Map;

public class ClassIdGenerator {

	private static final ClassIdGenerator instance = new ClassIdGenerator();
	
	private Map<String, BigInteger> ids = new HashMap<String, BigInteger>();
	private int id = 1;
	
	private ClassIdGenerator() {}
	
	public static ClassIdGenerator getInstance(){
		return instance;
	}
	
	public BigInteger getClassId(String className){
		if (!ids.containsKey(className))
			ids.put(className, BigInteger.valueOf(id++));
		return ids.get(className);
	}
}
