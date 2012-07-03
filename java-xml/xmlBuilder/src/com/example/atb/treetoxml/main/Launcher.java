package com.example.atb.treetoxml.main;

import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Collection;
import java.util.LinkedList;

import javax.tools.JavaFileObject;
import javax.xml.stream.XMLStreamException;

import com.example.atb.core.BypassException;
import com.example.atb.core.TraversalHandler;
import com.example.atb.main.Main;
import com.example.atb.treetoxml.XMLRepresentation;
import com.example.atb.treetoxml.stax.StaxXmlRepresentation;

/**
 * Класс утилиты командной строки для получения AST в виде XML
 * из исходного кода на Java.
 * 
 * @author mz
 *
 */
public class Launcher {
	private static String PATH = "../test";
	
	public static void main(String[] argv) throws BypassException, IOException, XMLStreamException {
		System.out.println("Using '"+PATH+"' project dir");
		Main main = Main.getInstance(PATH);
		Iterable<? extends JavaFileObject> units = main.getUnits();
		for (JavaFileObject unit : units) {
			System.out.println("Processing file: "+unit.getName());
			Collection<TraversalHandler> handlers = new LinkedList<TraversalHandler>();
			XMLRepresentation toXML = new XMLRepresentation(true, true);
			StaxXmlRepresentation stax = StaxXmlRepresentation.getInstance(unit.getName()+".stax.xml");
			handlers.add(toXML);
			handlers.add(stax);
			stax.startDocument();
			main.execute(unit, handlers);
			stax.endDocument();
			System.out.println("Writing result to XML: "+unit.getName() + ".xml");
			FileOutputStream fos = new FileOutputStream(unit.getName() + ".xml");
			fos.write(toXML.toString().getBytes());
			fos.flush();
			fos.close();
		}
	}

}
