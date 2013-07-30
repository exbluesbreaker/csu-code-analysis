package ru.csu.stan.ui.code;

import java.io.File;
import java.io.FileNotFoundException;
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
	
	public void processFiles(String projectRoot, String outRoot) throws FileNotFoundException{
		File src = new File(projectRoot);
		File outFile = new File(outRoot);
		if (!src.exists())
			throw new FileNotFoundException(projectRoot);
		if (!outFile.exists())
			throw new FileNotFoundException(outRoot);
	}
	
}
