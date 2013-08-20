package ru.csu.stan.ui.code;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

import javax.annotation.processing.FilerException;

import ru.csu.stan.java.classgen.jaxb.BaseElement;

/**
 * Проект, в котором расставляются якоря.
 * Собирает информацию о якорях на основе XML-элементов и соответствующих имен файлов.
 * 
 * @author mz
 *
 */
public class Project {
	
    private static final String JS_EXTENSION = ".js";
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
	
	public void addAnchor(String filename, BaseElement element, String id){
		if (element.getFromlineno() != null && element.getFromlineno().intValue() > 0 && element.getColOffset() != null && element.getColOffset().intValue() > 0)
			this.getFile(filename).createAnchor(element.getFromlineno().intValue(), element.getColOffset().intValue(), element.getName(), id);
	}
	
	public void processFiles(String projectRoot, String outRoot) throws FileNotFoundException, FilerException, IOException{
		File src = new File(projectRoot);
		File outFile = new File(outRoot);
		if (!src.exists())
			throw new FileNotFoundException(projectRoot);
		if (!src.isDirectory())
			throw new FilerException(src + " is not a directory.");
		if (!outFile.exists())
			throw new FileNotFoundException(outRoot);
		if (!outFile.isDirectory())
			throw new FilerException(outFile + " is not a directory.");
		for (Entry<String, SourceFile> file: files.entrySet()){
			file.getValue().processFile(getSourceFile(src, file.getKey()), getDestinationFile(outFile, file.getKey()));
		}
	}
	
	private File getSourceFile(File projectRoot, String filename) throws FileNotFoundException{
		File result = new File(projectRoot, filename);
		if (result.exists())
			return result;
		else
			throw new FileNotFoundException(filename);
	}
	
	private File getDestinationFile(File resultRoot, String filename) throws IOException{
		File result = new File(resultRoot, changeFileExtension(filename));
		result.getParentFile().mkdirs();
		result.createNewFile();
		return result;
	}
	
	private String changeFileExtension(String filename){
	    StringBuffer sb = new StringBuffer(filename);
	    if (sb.lastIndexOf(".") > 0)
	        sb.delete(sb.lastIndexOf("."), sb.length());
	    sb.append(JS_EXTENSION);
	    return sb.toString();
	}
}
