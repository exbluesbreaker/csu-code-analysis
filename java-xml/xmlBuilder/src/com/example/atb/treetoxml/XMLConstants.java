package com.example.atb.treetoxml;

import com.example.atb.core.resources.ResourceManager;
import com.sun.tools.javac.code.Symbol;
import com.sun.tools.javac.code.Type;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.util.Name;

public class XMLConstants {

	private XMLConstants() {
	}

	public static String SymbolToString(Symbol symbol) {
		return symbol.toString();
	}

	public static String NameToString(Name name) {
		return name.toString();
	}

	public static String getIntegerToHex(int val) {
		StringBuilder sb = new StringBuilder(Integer.toHexString(val));
		if (sb.length() < 8) {
			for (int i = 0; i < 8 - sb.length(); i++) {
				sb.insert(0, '0');
			}
		}
		return sb.toString();
	}

	public static String getLongToHex(long val) {
		StringBuilder sb = new StringBuilder(Long.toHexString(val));
		if (sb.length() < 16) {
			for (int i = 0; i < 16 - sb.length(); i++) {
				sb.insert(0, '0');
			}
		}
		return sb.toString();
	}

	public static String TypeToString(Type type) {
		return String.valueOf(type);
	}

	public static String getObjectToString(Object obj) {
		if (obj == null) {
			return String.valueOf(obj);
		}
		return new StringBuilder().append('"').append(String.valueOf(obj))
				.append('"').toString();
	}

	public static String getNodeTagName(Class<? extends JCTree> nodeClass) {
		String fromResource = ResourceManager.getResourceString(nodeClass
				.getName());
		return fromResource != null ? fromResource : nodeClass.getName();
	}
}
