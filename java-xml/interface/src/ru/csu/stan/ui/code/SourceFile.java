package ru.csu.stan.ui.code;

import java.util.LinkedList;
import java.util.List;

/**
 * Класс, определяющий файл исходного кода, в котором необходимо расставить якоря для навигации.
 * 
 * @author mz
 *
 */
public class SourceFile {
	
	private String filename;
	private List<Anchor> anchorList = new LinkedList<Anchor>();
	
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
	
	public void createAnchor(int line, int col){
		addAnchor(Anchor.createInstance(line, col));
	}
}
