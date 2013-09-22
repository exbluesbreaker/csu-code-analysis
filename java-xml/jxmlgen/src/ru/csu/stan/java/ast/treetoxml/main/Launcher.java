package ru.csu.stan.java.ast.treetoxml.main;

import java.io.IOException;
import java.util.Collection;
import java.util.LinkedList;

import javax.tools.JavaFileObject;
import javax.xml.stream.XMLStreamException;

import ru.csu.stan.java.ast.core.BypassException;
import ru.csu.stan.java.ast.core.TraversalHandler;
import ru.csu.stan.java.ast.main.Main;
import ru.csu.stan.java.ast.treetoxml.stax.StaxXmlRepresentation;


/**
 * Класс утилиты командной строки для получения AST в виде XML
 * из исходного кода на Java.
 * 
 * @author mz
 *
 */
public class Launcher {
	private static final String HELP = "USAGE: ast <project dir> <output file>";
	
	public static void main(String[] args) throws BypassException, IOException, XMLStreamException {
		if (args != null && args.length > 0 && args.length < 3){
			final String path = args[0];
			final String out = args[1];
			System.out.println("Using "+path+" as project dir");
			Main main = Main.getInstance(path);
			
			Collection<TraversalHandler> handlers = new LinkedList<TraversalHandler>();
			System.out.println("Using " + out + " as output file");
			StaxXmlRepresentation stax = StaxXmlRepresentation.getInstance(path, out);
			handlers.add(stax);
			stax.startDocument();
			
			Iterable<? extends JavaFileObject> units = main.getUnits();
			for (JavaFileObject unit : units) {
				System.out.println("Processing file: "+unit.getName());
				main.execute(unit, handlers);
			}
			stax.endDocument();
			System.out.println("Successfully ended");
		}
		else
			System.out.println(HELP);
	}

}
