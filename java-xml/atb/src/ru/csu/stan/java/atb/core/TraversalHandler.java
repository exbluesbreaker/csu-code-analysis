package ru.csu.stan.java.atb.core;

import java.util.List;

import javax.lang.model.type.TypeKind;
import javax.tools.JavaFileObject;

import com.sun.source.tree.Tree.Kind;
import com.sun.tools.javac.code.BoundKind;
import com.sun.tools.javac.code.Symbol;
import com.sun.tools.javac.code.Type;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.util.Name;

/**
 * Интерфейс, описывающий события, возникающие при обходе AST.
 *
 */
public interface TraversalHandler {
    
	/**
	 * Событие, возникающее при начале обработки узла.
	 */
    public void onStartNode(JCTree node, String name, Position position);
    
    /**
     * Событие, возникающее в конце обработки узла.
     */
    public void onEndNode(JCTree node, String name, Position position);
    
    /**
     * Событие, возникающее, когда узел - null.
     */
    public void onNullNode(String name);
    
    /**
     * Событие, возникающее в начале обработки списка узлов.
     */
    public void onStartNodesList(List<? extends JCTree> nodesList, String name);
    
    /**
     * Событие, возникающее в конце обработки списка узлов.
     */
    public void onEndNodesList(List<? extends JCTree> nodesList, String name);
    
    /**
     * Событие, возникающее, когда список узлов - null.
     */
    public void onNullNodesList(String name);
    
    /**
     * Событие, возникающее в начале обработки символа.
     */
    public void onSymbolStart(Symbol symbol, String name);
    
    /**
     * Событие, возникающее в конце обработки символа.
     */
    public void onSymbolEnd(Symbol symbol, String name);
    
    /**
     * Событие, возникающее, когда символ - null.
     */
    public void onNullSymbol(String name);
    
    /**
     * Событие, возникающее при обработки строки компилятора.
     */
    public void onName(Name nameElement, String name);
    
    /**
     * Событие, возникающее при обработке литерала.
     */
    public void onLiteral(Object value, Kind valueType);
    
    /**
     * Событие, возникающее при обработке типа.
     */
    public void onType(Type type, String name);
    
    /**
     * Событие, возникающее при обработке флагов.
     */
    public void onFlags(long flags);
    
    /**
     * Событие, возникающее при обработке примитивного типа.
     */
    public void onPrimitiveType(TypeKind typeKind);
    
    /**
     * Событие, возникающее при обработке пустого оператора.
     */
    public void onEmptyStatement();
    
    /**
     * Событие, возникающее при обработке типа ограничения в generic-конструкциях.
     */
    public void onBoundKind(BoundKind boundKind);
    
    /**
     * Событие, возникающее при ошибке.
     */
    public void onErrorOcured(Exception e);
    
    /**
     * Событие, возникающее при обработке файла с исходным кодом.
     * Нужно чтобы отразить файл в представлении, то есть, не является стартовым.
     */
    public void onSourceFile(JavaFileObject sourceFile);
    
    /**
     * Интерфейс, описывающий позицию конструкции в исходном тексте.
     *
     */
    public static interface Position {
        
    	/**
    	 * 
    	 * @return Номер строки.
    	 */
        public int getLineNumber();
        
        /**
         * 
         * @return Номер символа в строке.
         */
        public int getColumnNumber();
    }

}
