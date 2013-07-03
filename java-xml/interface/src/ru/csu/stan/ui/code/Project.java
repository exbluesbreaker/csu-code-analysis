package ru.csu.stan.ui.code;

import java.util.HashMap;
import java.util.Map;

import ru.csu.stan.java.classgen.jaxb.BaseElement;

public class Project {

	private Map<String, SourceFile> files = new HashMap<String, SourceFile>();

	private Project() {}
	
	public static Project createInstance(){
		return new Project();
	}
	
	public SourceFile getFile(String filename){
		if (!files.containsKey(filename))
			files.put(filename, SourceFile.getInstance(filename));
		return files.get(filename);
	}
	
	public void addAnchor(String filename, BaseElement element){
		this.getFile(filename).createAnchor(element.getFromlineno().intValue(), element.getColOffset().intValue());
	}
	
}
