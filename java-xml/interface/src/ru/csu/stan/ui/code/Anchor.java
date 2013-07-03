package ru.csu.stan.ui.code;

/**
 * Якорь, который необходимо поставить в исходном коде.
 * 
 * @author mz
 *
 */
public class Anchor {

	private int line;
	private int col;
	
	private Anchor(int line, int col){
		this.line = line;
		this.col = col;
	}
	
	static Anchor createInstance(int line, int col){
		return new Anchor(line, col);
	}
	
	public int getLine() {
		return line;
	}
	
	public void setLine(int line) {
		this.line = line;
	}
	
	public int getCol() {
		return col;
	}
	
	public void setCol(int col) {
		this.col = col;
	}
	
}
