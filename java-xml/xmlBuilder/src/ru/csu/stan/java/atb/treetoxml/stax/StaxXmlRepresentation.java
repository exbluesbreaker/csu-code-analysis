package ru.csu.stan.java.atb.treetoxml.stax;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.util.List;

import javax.lang.model.type.TypeKind;
import javax.xml.stream.XMLOutputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;

import org.apache.commons.lang3.StringUtils;

import ru.csu.stan.java.atb.core.ContentAssistant;
import ru.csu.stan.java.atb.core.TraversalHandler;

import com.sun.source.tree.Tree.Kind;
import com.sun.tools.javac.code.BoundKind;
import com.sun.tools.javac.code.Flags;
import com.sun.tools.javac.code.Symbol;
import com.sun.tools.javac.code.Type;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.util.Name;

/**
 * Вывод AST в виде XML с использованием StAX.
 * 
 * @author mz
 *
 */
public class StaxXmlRepresentation implements TraversalHandler {

	private static String NEW_LINE = "\n";
	private static String TAB = "   ";
	private int offset;
	private XMLStreamWriter writer;
	
	private StaxXmlRepresentation() {}
	
	public static StaxXmlRepresentation getInstance(String filename) throws FileNotFoundException, XMLStreamException{
		StaxXmlRepresentation representation = new StaxXmlRepresentation();
		XMLOutputFactory factory = XMLOutputFactory.newInstance();
		File f = new File(filename);
		FileOutputStream stream = new FileOutputStream(f);
		representation.writer = factory.createXMLStreamWriter(stream);
		return representation;
	}
	
	@Override
	public void onStartNode(JCTree node, String name, Position position) {
		try {
			writeOffset();
			this.writer.writeStartElement(ContentAssistant.getNodeName(ContentAssistant.getTagNameByTreeElementKind(node.getKind())));
			this.writer.writeAttribute("line", String.valueOf(position.getLineNumber()));
			this.writer.writeAttribute("col", String.valueOf(position.getColumnNumber()));
			this.offset++;
		} catch (XMLStreamException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public void onEndNode(JCTree node, String name, Position position) {
		try {
			this.offset--;
			writeOffset();
			this.writer.writeEndElement();
		} catch (XMLStreamException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public void onNullNode(String name) {
		
	}

	@Override
	public void onStartNodesList(List<? extends JCTree> nodesList, String name) {
		try {
			writeOffset();
			this.writer.writeStartElement(name);
			this.offset++;
		} catch (XMLStreamException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public void onEndNodesList(List<? extends JCTree> nodesList, String name) {
		try {
			this.offset--;
			writeOffset();
			this.writer.writeEndElement();
		} catch (XMLStreamException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public void onNullNodesList(String name) {
		
	}

	@Override
	public void onSymbolStart(Symbol symbol, String name) {
		
	}

	@Override
	public void onSymbolEnd(Symbol symbol, String name) {
		
	}

	@Override
	public void onNullSymbol(String name) {
		
	}

	@Override
	public void onName(Name nameElement, String name) {
		try {
			writer.writeAttribute("name", String.valueOf(nameElement));
		} catch (XMLStreamException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public void onLiteral(Object value, Kind valueType) {
		String type = null;
		switch (valueType) {
		case INT_LITERAL:
			type = "int";
			break;
		case DOUBLE_LITERAL:
			type = "double";
			break;
		case LONG_LITERAL:
			type = "long";
			break;
		case CHAR_LITERAL:
			type = "char";
			break;
		case STRING_LITERAL:
			type = "string";
			break;
		case BOOLEAN_LITERAL:
			type = "boolean";
			break;
		case FLOAT_LITERAL:
			type = "float";
			break;
		case NULL_LITERAL:
			type = "null";
			break;
		default:
			type = "undefined";
		}
		try {
			this.writer.writeAttribute("type", type);
			this.writer.writeAttribute("value", String.valueOf(value));
		} catch (XMLStreamException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public void onType(Type type, String name) {
		
	}

	@Override
	public void onFlags(long flags) {
		try {
		String[] flagArray = StringUtils.split(Flags.toString(flags));
		for (String flagName : flagArray){
			writeOffset();
			this.writer.writeStartElement("modifier");
			this.writer.writeAttribute("name", flagName);
			this.writer.writeEndElement();
		}
		} catch (XMLStreamException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public void onPrimitiveType(TypeKind typeKind) {
		try {
			this.writer.writeAttribute("name", String.valueOf(typeKind).toLowerCase());
		} catch (XMLStreamException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public void onEmptyStatement() {
		
	}

	@Override
	public void onBoundKind(BoundKind boundKind) {
		
	}

	@Override
	public void onErrorOcured(Exception e) {
		
	}
	
	private void writeOffset(){
		try {
			writer.writeCharacters(NEW_LINE);
			for (int i = 0; i < offset; i++)
				this.writer.writeCharacters(TAB);
		} catch (XMLStreamException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public void startDocument(){
		try {
			writer.writeStartDocument();
			this.writer.writeCharacters(NEW_LINE);
		} catch (XMLStreamException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public void endDocument(){
		try {
			writer.writeEndDocument();
			writer.close();
		} catch (XMLStreamException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}
