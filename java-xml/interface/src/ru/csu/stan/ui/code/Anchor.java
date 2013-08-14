package ru.csu.stan.ui.code;

import java.text.MessageFormat;

/**
 * Якорь, который необходимо поставить в исходном коде.
 * 
 * @author mz
 *
 */
public class Anchor {

	private static final String OPENING_A_TEMPLATE = "<a name=\"{0}\">";
	private static final String CLOSING_A = "</a>";

	private int line;
	private int col;
	private String name;
	private String id;
	
	private Anchor(int line, int col, String name, String id){
		this.line = line;
		this.col = col;
		this.name = name;
		this.id = id;
	}
	
	static Anchor createInstance(int line, int col, String name, String id){
		return new Anchor(line, col, name, id);
	}
	
	public int getLine() {
		return line;
	}
	
	public int getCol() {
		return col;
	}
	
	public String processLine(String line){
		StringBuffer sb = new StringBuffer(line);
		int startPosition = sb.indexOf(getNameWithoutDots(), col-1);
		int endPosition;
		if (startPosition < 0){
			startPosition = col - 1;
			endPosition = getFirstNonLetterChar(sb, col);
		}
		else
			endPosition = getNameWithoutDots().length() + startPosition;
		sb.insert(endPosition, CLOSING_A);
		sb.insert(startPosition, MessageFormat.format(OPENING_A_TEMPLATE, id));
		return sb.toString();
	}
	
	public String getNameWithoutDots(){
		int dot = name.lastIndexOf('.');
		if (dot >= 0)
			return name.substring(dot+1);
		else
			return name;
	}
	
	private int getFirstNonLetterChar(StringBuffer sb, int fromIndex){
		for (int i = fromIndex; i < sb.length(); i++){
			if ((sb.charAt(i) < 'a' || sb.charAt(i) > 'z') && (sb.charAt(i) < 'A' || sb.charAt(i) > 'Z'))
				return i;
		}
		return fromIndex;
	}
}
