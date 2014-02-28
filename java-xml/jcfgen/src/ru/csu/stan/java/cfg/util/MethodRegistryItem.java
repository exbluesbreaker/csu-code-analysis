package ru.csu.stan.java.cfg.util;

import java.util.HashSet;
import java.util.Set;

/**
 * 
 * @author mz
 *
 */
public class MethodRegistryItem {
	private String name;
	private int id;
	private Set<String> args = new HashSet<String>();
	
	public String getName() {
		return name;
	}
	
	public void setName(String name) {
		this.name = name;
	}
	
	public int getId() {
		return id;
	}
	
	public void setId(int id) {
		this.id = id;
	}
	
	public Set<String> getArgs() {
		return args;
	}
	
	
	public void addArg(String arg){
		args.add(arg);
	}
	
}
