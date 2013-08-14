package ru.csu.stan.ui.code;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.text.MessageFormat;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

/**
 * Класс, определяющий файл исходного кода, в котором необходимо расставить якоря для навигации.
 * Позволяет обработать исходный файл и вывести результат в JavaScript-файл.
 * 
 * @author mz
 *
 */
public class SourceFile {
	
	private String filename;
	private List<Anchor> anchorList = new LinkedList<Anchor>();
	private static final String LINE_SEPARATOR = System.getProperty("line.separator");
	private static final String JS_LINE_SEPARATOR = "\\n\\";
	private static final String JS_FUNCTION_BEGIN_TEMPLATE = "sourceFiles.{0} = function(){\n  return \"";
	private static final String JS_FUNCTION_END = "\";\n}\n";
	private static final String JS_ENSURE_PACKAGE_EXIST = "if (typeof sourceFiles.{0} == 'undefined')\n  sourceFiles.{0} = '{}';\n\n";
	
	private SourceFile(String filename) {
		this.filename = filename;
	}
	
	static SourceFile getInstance(String filename){
		return new SourceFile(filename);
	}
	
	public String getFilename() {
		return filename;
	}
	
	public void setFilename(String filename) {
		this.filename = filename;
	}
	
	public List<Anchor> getAnchorList() {
		return anchorList;
	}
	
	public void addAnchor(Anchor anchor) {
		this.anchorList.add(anchor);
	}
	
	public void createAnchor(int line, int col, String name, String id){
		addAnchor(Anchor.createInstance(line, col, name, id));
	}
	
	public void processFile(File src, File dst) throws FileNotFoundException, IOException{
		if (anchorList.isEmpty())
			return;
		Collections.sort(anchorList, new AnchorComparator());
		BufferedReader reader = new BufferedReader(new FileReader(src));
		BufferedWriter writer = new BufferedWriter(new FileWriter(dst));
		String line;
		int lineNumber = 1;
		Iterator<Anchor> it = anchorList.iterator();
		Anchor anchor = it.next();
		writeJSPackageEnsurance(writer);
		writer.write(MessageFormat.format(JS_FUNCTION_BEGIN_TEMPLATE, getFilePackageName()));
		while ((line = reader.readLine()) != null){
			while (anchor != null && anchor.getLine() == lineNumber){
				line = anchor.processLine(line);
				if (it.hasNext())
					anchor = it.next();
				else
					anchor = null;
			}
			writer.write(line.replaceAll("\"", "\\\\\""));
			writer.write(JS_LINE_SEPARATOR);
			writer.write(LINE_SEPARATOR);
			lineNumber++;
		}
		writer.write(JS_FUNCTION_END);
		reader.close();
		writer.close();
	}
	
	private void writeJSPackageEnsurance(Writer writer) throws IOException{
	    String packageName = filename.replaceAll(System.getProperty("file.separator"), ".");
	    String[] packages = packageName.split(".");
	    String current = "";
	    if (packages.length > 2)
	        for (int i = 0; i < packages.length - 2; i++)
	        {
	            current += packages[i];
	            writer.write(MessageFormat.format(JS_ENSURE_PACKAGE_EXIST, current));
	            current += '.';
	        }
	}
	
	private String getFilePackageName(){
	    StringBuffer sb = new StringBuffer(filename.replaceAll(System.getProperty("file.separator"), "."));
	    if (sb.charAt(0) == '.')
	        sb.deleteCharAt(0);
	    if (sb.lastIndexOf(".") > 0)
	        sb.delete(sb.lastIndexOf("."), sb.length());
	    return sb.toString();
	}
}
