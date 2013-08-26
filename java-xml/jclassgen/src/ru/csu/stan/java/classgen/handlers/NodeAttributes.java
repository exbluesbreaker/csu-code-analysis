package ru.csu.stan.java.classgen.handlers;

import java.util.Iterator;

import javax.xml.namespace.QName;
import javax.xml.stream.events.Attribute;
import javax.xml.stream.events.StartElement;

/**
 * 
 * @author mz
 *
 */
public class NodeAttributes {
	
	public static final String NAME_ATTRIBUTE = "name";
	public static final String FILENAME_ATTRIBUTE = "filename";
	public static final String LINE_ATTRIBUTE = "line";
	public static final String COL_ATTRIBUTE = "col";

	private StartElement event;
	
	public NodeAttributes(StartElement event){
		this.event = event;
	}
	
	public boolean isAttributeExist(String name){
		for (@SuppressWarnings("unchecked") Iterator<Attribute> it = event.getAttributes(); it.hasNext(); )
			if (it.next().getName().equals(name))
				return true;
		return false;
	}
	
	public String getStringAttribute(String name){
		Attribute attr = event.getAttributeByName(QName.valueOf(name));
		if (attr != null)
			return attr.getValue();
		else
			return "";
	}
	
	public int getIntAttribute(String name){
		String str = getStringAttribute(name);
		try{
			return Integer.parseInt(str);
		}
		catch (NumberFormatException e){
			e.printStackTrace();
			return 0;
		}
	}
	
	public String getNameAttribute(){
		return getStringAttribute(NAME_ATTRIBUTE);
	}
}
