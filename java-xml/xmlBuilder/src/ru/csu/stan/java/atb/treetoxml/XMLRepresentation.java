package ru.csu.stan.java.atb.treetoxml;

import java.util.Collection;
import java.util.LinkedList;
import java.util.List;

import javax.lang.model.type.TypeKind;

import ru.csu.stan.java.atb.core.TraversalHandler;

import com.sun.source.tree.Tree.Kind;
import com.sun.tools.javac.code.BoundKind;
import com.sun.tools.javac.code.Symbol;
import com.sun.tools.javac.code.Type;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.util.Name;

public class XMLRepresentation implements TraversalHandler {

	private static final String STRING_HEADER = "<?xml version='1.0' encoding='Windows-1251'?>";
	private static final String STRING_HTML_LESS = "&lt;";
	private static final String STRING_HTML_GREATER = "&gt;";
	private static final String STRING_LESS = "<";
	private static final String STRING_GREATER = ">";
	private static final String STRING_LINE = "line";
	private static final String STRING_FLAGS = "flags";
	private static final String STRING_COLUMN = "column";
	private static final String STRING_TYPE = "type";
	private static final String STRING_TYPE_NODE = "object";
	private static final String STRING_TYPE_NODES_LIST = "array";
	private static final String STRING_TYPE_SYMBOL = "symbol";
	private static final String STRING_TYPE_NAME = "name";
	private static final String STRING_TYPE_TYPE = "type";
	private static final String STRING_NULL = "null";

	private static final char CHAR_ENDL = '\n';
	private static final char CHAR_SPACE = ' ';
	private static final char CHAR_LESS = '<';
	private static final char CHAR_GREATER = '>';
	private static final char CHAR_SLASH = '/';
	private static final char CHAR_DOUBLE_QUOTE = '"';
	private static final char CHAR_EQUAL = '=';

	private final StringBuilder content = new StringBuilder();
	private final boolean isSeparateLines;
	private final boolean useNodeTypes;

	private final LinkedList<String> tags = new LinkedList<String>();

	public XMLRepresentation(boolean separateLines, boolean useNodeTypes) {
		isSeparateLines = separateLines;
		this.useNodeTypes = useNodeTypes;
		addLine(getHeader());
	}

	protected String getHeader() {
		return STRING_HEADER;
	}

	protected void addLine(String line) {
		content.append(line);
		if (isSeparateLines) {
			content.append(CHAR_ENDL);
		}
	}

	protected void startTag(String name, Collection<Attribute> attributes) {
		addLine(constructTag(name, true, attributes));
		tags.addLast(name);
	}

	protected void endTag() {
		addLine(constructTag(tags.removeLast(), false, null));
	}

	protected String constructTag(String name, boolean isOpenTag,
			Collection<Attribute> attributes) {
		String safeName = removeServiceCharacters(name);
		StringBuilder tag = new StringBuilder();
		tag.append(CHAR_LESS);
		if (!isOpenTag) {
			tag.append(CHAR_SLASH);
		}
		tag.append(safeName);
		if (attributes != null) {
			for (Attribute attr : attributes) {
				tag.append(CHAR_SPACE)
						.append(removeServiceCharacters(attr.getKey()))
						.append(CHAR_EQUAL).append(CHAR_DOUBLE_QUOTE)
						.append(removeServiceCharacters(attr.getValue()))
						.append(CHAR_DOUBLE_QUOTE);
			}
		}
		tag.append(CHAR_GREATER);
		return tag.toString();
	}

	protected String removeServiceCharacters(String target) {
		return target.replaceAll(STRING_LESS, STRING_HTML_LESS)
				.replaceAll(STRING_GREATER, STRING_HTML_GREATER)
				.replaceAll("\\$", ".");
	}

	@Override
	public void onStartNode(JCTree node, String name, Position position) {
		Collection<Attribute> nameAttributes = null;
		if (useNodeTypes) {
			nameAttributes = new LinkedList<XMLRepresentation.Attribute>();
			nameAttributes.add(new Attribute(STRING_TYPE, STRING_TYPE_NODE));
		}
		startTag(name, nameAttributes);
		if (node != null) {
			Collection<Attribute> mainNodeattributes = new LinkedList<Attribute>(
					positionToAttributes(position));
			startTag(XMLConstants.getNodeTagName(node.getClass()),
					mainNodeattributes);
		}
	}

	@Override
	public void onEndNode(JCTree node, String name, Position position) {
		endTag();
		if (node != null) {
			endTag();
		}
	}

	@Override
	public void onNullNode(String name) {
		onStartNode(null, name, null);
		addLine(STRING_NULL);
		onEndNode(null, name, null);
	}

	@Override
	public void onStartNodesList(List<? extends JCTree> nodesList, String name) {
		Collection<Attribute> nameAttributes = null;
		if (useNodeTypes) {
			nameAttributes = new LinkedList<XMLRepresentation.Attribute>();
			nameAttributes.add(new Attribute(STRING_TYPE,
					STRING_TYPE_NODES_LIST));
		}
		startTag(name, nameAttributes);
	}

	@Override
	public void onEndNodesList(List<? extends JCTree> nodesList, String name) {
		endTag();
	}

	@Override
	public void onNullNodesList(String name) {
		onStartNodesList(null, name);
		addLine(STRING_NULL);
		onEndNodesList(null, name);
	}

	@Override
	public void onSymbolStart(Symbol symbol, String name) {
		Collection<Attribute> nameAttributes = null;
		if (useNodeTypes) {
			nameAttributes = new LinkedList<XMLRepresentation.Attribute>();
			nameAttributes.add(new Attribute(STRING_TYPE, STRING_TYPE_SYMBOL));
		}
		startTag(name, nameAttributes);
		if (symbol != null) {
			addLine(removeServiceCharacters(symbol.toString()));
		}
	}

	@Override
	public void onSymbolEnd(Symbol symbol, String name) {
		endTag();
	}

	@Override
	public void onNullSymbol(String name) {
		onSymbolStart(null, name);
		addLine(STRING_NULL);
		onSymbolEnd(null, name);
	}

	@Override
	public void onName(Name nameElement, String name) {
		Collection<Attribute> nameAttributes = null;
		if (useNodeTypes) {
			nameAttributes = new LinkedList<XMLRepresentation.Attribute>();
			nameAttributes.add(new Attribute(STRING_TYPE, STRING_TYPE_NAME));
		}
		startTag(name, nameAttributes);
		addLine(removeServiceCharacters(nameElement.toString()));
		endTag();
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
		startTag(type, null);
		addLine(String.valueOf(value));
		endTag();
	}

	@Override
	public void onType(Type type, String name) {
		Collection<Attribute> nameAttributes = null;
		if (useNodeTypes) {
			nameAttributes = new LinkedList<XMLRepresentation.Attribute>();
			nameAttributes.add(new Attribute(STRING_TYPE, STRING_TYPE_TYPE));
		}
		startTag(name, nameAttributes);
		addLine(String.valueOf(type));
		endTag();
	}

	@Override
	public void onFlags(long flags) {
		startTag(STRING_FLAGS, null);
		StringBuilder sb = new StringBuilder(Long.toHexString(flags));
		if (sb.length() < 16) {
			for (int i = 0; i < 16 - sb.length(); i++) {
				sb.insert(0, '0');
			}
		}
		addLine(sb.toString());
		endTag();
	}

	@Override
	public void onPrimitiveType(TypeKind typeKind) {
		addLine(String.valueOf(typeKind));
	}

	@Override
	public void onEmptyStatement() {
		addLine(";");
	}

	@Override
	public void onBoundKind(BoundKind boundKind) {
		addLine(String.valueOf(boundKind));
	}

	@Override
	public void onErrorOcured(Exception e) {
		System.out.println(e);
	}

	protected Collection<Attribute> positionToAttributes(Position position) {
		Collection<Attribute> attrs = new LinkedList<Attribute>();
		attrs.add(new Attribute(STRING_LINE, String.valueOf(position
				.getLineNumber())));
		attrs.add(new Attribute(STRING_COLUMN, String.valueOf(position
				.getColumnNumber())));
		return attrs;
	}

	protected static class Attribute {
		private final String key;
		private final String value;

		public Attribute(String key, String value) {
			this.key = key;
			this.value = value;
		}

		public String getKey() {
			return key;
		}

		public String getValue() {
			return value;
		}
	}

	@Override
	public String toString() {
		return content.toString();
	}

}
