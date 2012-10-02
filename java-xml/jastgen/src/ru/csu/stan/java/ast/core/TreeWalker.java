package ru.csu.stan.java.ast.core;

import java.util.List;

import javax.lang.model.type.TypeKind;
import javax.tools.JavaFileObject;

import com.sun.tools.javac.code.Symbol;
import com.sun.tools.javac.code.Type;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.util.Name;

/**
 * Интерфейс, описывающий поситителя, обходящего дерево.
 *
 */
public interface TreeWalker {
	
	/**
	 * Обработка "символа".
	 */
	void handle(Symbol symbol, String innerName);
	
	/**
	 * Обработка "типа".
	 */
	void handle(Type type, String innerName);
	
	/**
	 * Обработка "имени" - внутренней строки компилятора.
	 */
	void handle(Name nameElement, String innerName);
	
	/**
	 * Обработка узла AST.
	 */
	void handle(JCTree node, String innerName);
	
	/**
	 * Обработка списка узлов AST.
	 */
	void handle(List<? extends JCTree> nodesList, String innerName);
	
	/**
	 * Обработка флагов.
	 */
	void handleFlags(long flags);
	
	/**
	 * Обработка примитивного типа.
	 */
	void handlePrimitiveType(TypeKind typeKind);
	
	/**
	 * Обработка Java-файла с исходным кодом.
	 */
	void handleSourceFile(JavaFileObject javaFile);

}
