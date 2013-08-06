package ru.csu.stan.java.ast.main;

import java.lang.reflect.Constructor;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import javax.lang.model.type.TypeKind;
import javax.tools.JavaFileObject;

import ru.csu.stan.java.ast.core.BypassException;
import ru.csu.stan.java.ast.core.ContentAssistant;
import ru.csu.stan.java.ast.core.Messages;
import ru.csu.stan.java.ast.core.TraversalHandler;
import ru.csu.stan.java.ast.core.TreeWalker;
import ru.csu.stan.java.ast.nodes.handlers.JCAnnotationHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCArrayAccessHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCArrayTypeTreeHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCAssertHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCAssignHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCAssignOpHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCBinaryHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCBlockHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCBreakHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCCaseHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCCatchHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCClassDeclHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCCompilationUnitHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCConditionalHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCContinueHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCDoWhileLoopHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCEnhancedForLoopHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCErroneousHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCExpressionStatementHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCFieldAccessHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCForLoopHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCIdentHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCIfHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCImportHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCInstanceOfHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCLabeledStatementHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCLiteralHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCMethodDeclHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCMethodInvocationHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCModifiersHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCNewArrayHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCNewClassHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCParensHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCPrimitiveTypeTreeHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCReturnHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCSkipHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCSwitchHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCSynchronizedHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCThrowHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCTreeHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCTryHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCTypeApplyHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCTypeCastHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCTypeParameterHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCUnaryHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCVariableDeclHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCWhileLoopHandler;
import ru.csu.stan.java.ast.nodes.handlers.JCWildcardHandler;
import ru.csu.stan.java.ast.nodes.handlers.LetExprHandler;
import ru.csu.stan.java.ast.nodes.handlers.TypeBoundKindHandler;
import ru.csu.stan.java.ast.symbols.handlers.SymbolHandler;

import com.sun.source.tree.Tree.Kind;
import com.sun.tools.javac.code.BoundKind;
import com.sun.tools.javac.code.Symbol;
import com.sun.tools.javac.code.Type;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCAnnotation;
import com.sun.tools.javac.tree.JCTree.JCArrayAccess;
import com.sun.tools.javac.tree.JCTree.JCArrayTypeTree;
import com.sun.tools.javac.tree.JCTree.JCAssert;
import com.sun.tools.javac.tree.JCTree.JCAssign;
import com.sun.tools.javac.tree.JCTree.JCAssignOp;
import com.sun.tools.javac.tree.JCTree.JCBinary;
import com.sun.tools.javac.tree.JCTree.JCBlock;
import com.sun.tools.javac.tree.JCTree.JCBreak;
import com.sun.tools.javac.tree.JCTree.JCCase;
import com.sun.tools.javac.tree.JCTree.JCCatch;
import com.sun.tools.javac.tree.JCTree.JCClassDecl;
import com.sun.tools.javac.tree.JCTree.JCCompilationUnit;
import com.sun.tools.javac.tree.JCTree.JCConditional;
import com.sun.tools.javac.tree.JCTree.JCContinue;
import com.sun.tools.javac.tree.JCTree.JCDoWhileLoop;
import com.sun.tools.javac.tree.JCTree.JCEnhancedForLoop;
import com.sun.tools.javac.tree.JCTree.JCErroneous;
import com.sun.tools.javac.tree.JCTree.JCExpressionStatement;
import com.sun.tools.javac.tree.JCTree.JCFieldAccess;
import com.sun.tools.javac.tree.JCTree.JCForLoop;
import com.sun.tools.javac.tree.JCTree.JCIdent;
import com.sun.tools.javac.tree.JCTree.JCIf;
import com.sun.tools.javac.tree.JCTree.JCImport;
import com.sun.tools.javac.tree.JCTree.JCInstanceOf;
import com.sun.tools.javac.tree.JCTree.JCLabeledStatement;
import com.sun.tools.javac.tree.JCTree.JCLiteral;
import com.sun.tools.javac.tree.JCTree.JCMethodDecl;
import com.sun.tools.javac.tree.JCTree.JCMethodInvocation;
import com.sun.tools.javac.tree.JCTree.JCModifiers;
import com.sun.tools.javac.tree.JCTree.JCNewArray;
import com.sun.tools.javac.tree.JCTree.JCNewClass;
import com.sun.tools.javac.tree.JCTree.JCParens;
import com.sun.tools.javac.tree.JCTree.JCPrimitiveTypeTree;
import com.sun.tools.javac.tree.JCTree.JCReturn;
import com.sun.tools.javac.tree.JCTree.JCSkip;
import com.sun.tools.javac.tree.JCTree.JCSwitch;
import com.sun.tools.javac.tree.JCTree.JCSynchronized;
import com.sun.tools.javac.tree.JCTree.JCThrow;
import com.sun.tools.javac.tree.JCTree.JCTry;
import com.sun.tools.javac.tree.JCTree.JCTypeApply;
import com.sun.tools.javac.tree.JCTree.JCTypeCast;
import com.sun.tools.javac.tree.JCTree.JCTypeParameter;
import com.sun.tools.javac.tree.JCTree.JCUnary;
import com.sun.tools.javac.tree.JCTree.JCVariableDecl;
import com.sun.tools.javac.tree.JCTree.JCWhileLoop;
import com.sun.tools.javac.tree.JCTree.JCWildcard;
import com.sun.tools.javac.tree.JCTree.LetExpr;
import com.sun.tools.javac.tree.JCTree.TypeBoundKind;
import com.sun.tools.javac.util.Name;
import com.sun.tools.javac.util.Position.LineMap;

public class TreeWalkerImpl implements TreeWalker, TraversalHandler {

	private final LineMap lineMap;
	private final JCTree root;

	private Collection<TraversalHandler> handlers = new HashSet<TraversalHandler>();

	public TreeWalkerImpl(JCTree root, LineMap lineMap) {
		if (lineMap == null) {
			throw new NullPointerException("Line map is null");
		}
		if (root == null) {
			throw new NullPointerException("Root is null");
		}
		this.root = root;
		this.lineMap = lineMap;
	}

	public void executeBypass() {
		handle(root, root.getClass().getCanonicalName());
	}

	public void addBypassHandler(TraversalHandler handler) {
		handlers.add(handler);
	}

	public void removeBypassHandler(TraversalHandler handler) {
		handlers.remove(handler);
	}

	public final void handle(Symbol symbol, String innerName) {
		handleSymbol(symbol, getNodeName(innerName));
	}

	public final void handle(Type type, String innerName) {
		onType(type, getNodeName(innerName));
	}

	public final void handle(Name nameElement, String innerName) {
		onName(nameElement, getNodeName(innerName));
	}

	public final void handle(JCTree node, String innerName) {
		onHandleNode(node, getNodeName(innerName));
	}

	public final void handle(List<? extends JCTree> nodesList, String innerName) {
		onHandleList(nodesList, getNodeName(innerName));
	}

	public final void handleFlags(long flags) {
		onFlags(flags);
	}

	public final void handlePrimitiveType(TypeKind typeKind) {
		onPrimitiveType(typeKind);
	}

	private void handleSymbol(Symbol symbol, String innerName) {
		if (symbol == null) {

		} else {
			onSymbolStart(symbol, innerName);
			try {
				SymbolHandler<? extends Symbol> handler = getHandler(symbol);
				handler.perform();
			} catch (BypassException e) {
				onErrorOcured(e);
			}
			onSymbolEnd(symbol, innerName);
		}
	}
	
	@Override
	public void handleSourceFile(JavaFileObject javaFile) {
		onSourceFile(javaFile);
	}

	protected void onHandleNode(JCTree node, String name) {
		if (node == null) {
			onNullNode(name);
		} else {
			Position position = PositionImpl.createPosition(lineMap, node.getPreferredPosition());
			onStartNode(node, name, position);
			if (JCLiteral.class.isInstance(node)) {
				onLiteral(JCLiteral.class.cast(node).getValue(), JCLiteral.class.cast(node).getKind());
			} else if (JCSkip.class.isInstance(node)) {
				onEmptyStatement();
			} else if (TypeBoundKind.class.isInstance(node)) {
				onBoundKind(TypeBoundKind.class.cast(node).kind);
			} else {
				try {
					JCTreeHandler handler = getHandler(node);
					handler.perform(node);
				} catch (BypassException e) {
					onErrorOcured(e);
				}
			}
			onEndNode(node, name, position);
		}
	}

	protected void onHandleList(List<? extends JCTree> nodesList, String name) {
		if (nodesList == null || nodesList.size() == 0) {
			onNullNodesList(name);
		} else {
			onStartNodesList(nodesList, name);
			int i = 0;
			for (JCTree node : nodesList) {
				onHandleNode(node, "I" + i++);
			}
			onEndNodesList(nodesList, name);
		}
	}

	@Override
	public void onType(Type type, String name) {
		for (TraversalHandler handler : handlers) {
			handler.onType(type, name);
		}
	}

	@Override
	public void onName(Name nameElement, String name) {
		for (TraversalHandler handler : handlers) {
			handler.onName(nameElement, name);
		}
	}

	@Override
	public void onSymbolStart(Symbol symbol, String name) {
		for (TraversalHandler handler : handlers) {
			handler.onSymbolStart(symbol, name);
		}
	}

	@Override
	public void onSymbolEnd(Symbol symbol, String name) {
		for (TraversalHandler handler : handlers) {
			handler.onSymbolEnd(symbol, name);
		}
	}

	@Override
	public void onNullSymbol(String name) {
		for (TraversalHandler handler : handlers) {
			handler.onNullSymbol(name);
		}
	}

	@Override
	public void onStartNode(JCTree node, String name, Position position) {
		for (TraversalHandler handler : handlers) {
			handler.onStartNode(node, name, position);
		}
	}

	@Override
	public void onEndNode(JCTree node, String name, Position position) {
		for (TraversalHandler handler : handlers) {
			handler.onEndNode(node, name, position);
		}
	}

	@Override
	public void onNullNode(String name) {
		for (TraversalHandler handler : handlers) {
			handler.onNullNode(name);
		}
	}

	@Override
	public void onStartNodesList(List<? extends JCTree> nodesList,
			String name) {
		for (TraversalHandler handler : handlers) {
			handler.onStartNodesList(nodesList, name);
		}
	}

	@Override
	public void onEndNodesList(List<? extends JCTree> nodesList, String name) {
		for (TraversalHandler handler : handlers) {
			handler.onEndNodesList(nodesList, name);
		}
	}

	@Override
	public void onNullNodesList(String name) {
		for (TraversalHandler handler : handlers) {
			handler.onNullNodesList(name);
		}
	}

	@Override
	public void onLiteral(Object value, Kind valueType) {
		for (TraversalHandler handler : handlers) {
			handler.onLiteral(value, valueType);
		}
	}

	@Override
	public void onEmptyStatement() {
		for (TraversalHandler handler : handlers) {
			handler.onEmptyStatement();
		}
	}

	@Override
	public void onFlags(long flags) {
		for (TraversalHandler handler : handlers) {
			handler.onFlags(flags);
		}
	}

	@Override
	public void onPrimitiveType(TypeKind primitiveType) {
		for (TraversalHandler handler : handlers) {
			handler.onPrimitiveType(primitiveType);
		}
	}

	@Override
	public void onBoundKind(BoundKind boundKind) {
		for (TraversalHandler handler : handlers) {
			handler.onBoundKind(boundKind);
		}
	}

	@Override
	public void onErrorOcured(Exception e) {
		for (TraversalHandler handler : handlers) {
			handler.onErrorOcured(e);
		}
	}
	
	@Override
	public void onSourceFile(JavaFileObject file) {
		for (TraversalHandler handler : handlers) {
			handler.onSourceFile(file);
		}
	}

	private String getNodeName(String innerName) {
		String name = ContentAssistant.getNodeName(innerName);
		if (name == null) {
			name = innerName;
		}
		return name;
	}

	@SuppressWarnings("unchecked")
	private <K extends Symbol> SymbolHandler<K> getHandler(K symbol)
			throws BypassException {
		Class<? extends SymbolHandler<?>> symbolHandlerClass = symbolsHandlers
				.get(symbol.getClass());
		if (symbolHandlerClass == null) {
			throw new BypassException(Messages.MESSAGE_ATB102E, symbol
					.getClass().getCanonicalName());
		}
		try {
			Constructor<? extends SymbolHandler<?>> constructor = symbolHandlerClass
					.getConstructor(TreeWalker.class, symbol.getClass());
			if (constructor == null) {
				throw new BypassException(Messages.MESSAGE_ATB103E, symbol
						.getClass().getCanonicalName());
			}
			return (SymbolHandler<K>) constructor.newInstance(this, symbol);
		} catch (Exception e) {
			throw new BypassException(Messages.MESSAGE_ATB103E, e, symbol
					.getClass().getCanonicalName());
		}
	}

	private static final Map<Class<? extends Symbol>, Class<? extends SymbolHandler<?>>> symbolsHandlers = new HashMap<Class<? extends Symbol>, Class<? extends SymbolHandler<?>>>();

	static {

	}

	private JCTreeHandler getHandler(JCTree node) throws BypassException {
		Class<? extends JCTreeHandler> handlerClass = nodeHandlers.get(node
				.getClass());
		if (handlerClass == null) {
			throw new BypassException(Messages.MESSAGE_ATB100E, node.getClass()
					.getCanonicalName());
		}
		try {
			Constructor<? extends JCTreeHandler> constructor = handlerClass
					.getConstructor(TreeWalker.class);
			if (constructor == null) {
				throw new BypassException(Messages.MESSAGE_ATB101E, node
						.getClass().getCanonicalName());
			}
			return constructor.newInstance(this);
		} catch (Exception e) {
			throw new BypassException(Messages.MESSAGE_ATB101E, e, node
					.getClass().getCanonicalName());
		}
	}

	private static final Map<Class<? extends JCTree>, Class<? extends JCTreeHandler>> nodeHandlers = new HashMap<Class<? extends JCTree>, Class<? extends JCTreeHandler>>();

	static {
		nodeHandlers.put(JCAnnotation.class, JCAnnotationHandler.class);
		nodeHandlers.put(JCArrayAccess.class, JCArrayAccessHandler.class);
		nodeHandlers.put(JCArrayTypeTree.class, JCArrayTypeTreeHandler.class);
		nodeHandlers.put(JCAssert.class, JCAssertHandler.class);
		nodeHandlers.put(JCAssign.class, JCAssignHandler.class);
		nodeHandlers.put(JCAssignOp.class, JCAssignOpHandler.class);
		nodeHandlers.put(JCBinary.class, JCBinaryHandler.class);
		nodeHandlers.put(JCBlock.class, JCBlockHandler.class);
		nodeHandlers.put(JCBreak.class, JCBreakHandler.class);
		nodeHandlers.put(JCCase.class, JCCaseHandler.class);
		nodeHandlers.put(JCCatch.class, JCCatchHandler.class);
		nodeHandlers.put(JCClassDecl.class, JCClassDeclHandler.class);
		nodeHandlers.put(JCCompilationUnit.class,
				JCCompilationUnitHandler.class);
		nodeHandlers.put(JCConditional.class, JCConditionalHandler.class);
		nodeHandlers.put(JCContinue.class, JCContinueHandler.class);
		nodeHandlers.put(JCDoWhileLoop.class, JCDoWhileLoopHandler.class);
		nodeHandlers.put(JCEnhancedForLoop.class,
				JCEnhancedForLoopHandler.class);
		nodeHandlers.put(JCErroneous.class, JCErroneousHandler.class);
		nodeHandlers.put(JCExpressionStatement.class,
				JCExpressionStatementHandler.class);
		nodeHandlers.put(JCFieldAccess.class, JCFieldAccessHandler.class);
		nodeHandlers.put(JCForLoop.class, JCForLoopHandler.class);
		nodeHandlers.put(JCIdent.class, JCIdentHandler.class);
		nodeHandlers.put(JCIf.class, JCIfHandler.class);
		nodeHandlers.put(JCImport.class, JCImportHandler.class);
		nodeHandlers.put(JCInstanceOf.class, JCInstanceOfHandler.class);
		nodeHandlers.put(JCLabeledStatement.class,
				JCLabeledStatementHandler.class);
		nodeHandlers.put(JCLiteral.class, JCLiteralHandler.class);
		nodeHandlers.put(JCMethodDecl.class, JCMethodDeclHandler.class);
		nodeHandlers.put(JCMethodInvocation.class,
				JCMethodInvocationHandler.class);
		nodeHandlers.put(JCModifiers.class, JCModifiersHandler.class);
		nodeHandlers.put(JCNewArray.class, JCNewArrayHandler.class);
		nodeHandlers.put(JCNewClass.class, JCNewClassHandler.class);
		nodeHandlers.put(JCParens.class, JCParensHandler.class);
		nodeHandlers.put(JCPrimitiveTypeTree.class,
				JCPrimitiveTypeTreeHandler.class);
		nodeHandlers.put(JCReturn.class, JCReturnHandler.class);
		nodeHandlers.put(JCSkip.class, JCSkipHandler.class);
		nodeHandlers.put(JCSwitch.class, JCSwitchHandler.class);
		nodeHandlers.put(JCSynchronized.class, JCSynchronizedHandler.class);
		nodeHandlers.put(JCThrow.class, JCThrowHandler.class);
		nodeHandlers.put(JCTry.class, JCTryHandler.class);
		nodeHandlers.put(JCTypeApply.class, JCTypeApplyHandler.class);
		nodeHandlers.put(JCTypeCast.class, JCTypeCastHandler.class);
		nodeHandlers.put(JCTypeParameter.class, JCTypeParameterHandler.class);
		nodeHandlers.put(JCUnary.class, JCUnaryHandler.class);
		nodeHandlers.put(JCVariableDecl.class, JCVariableDeclHandler.class);
		nodeHandlers.put(JCWhileLoop.class, JCWhileLoopHandler.class);
		nodeHandlers.put(JCWildcard.class, JCWildcardHandler.class);
		nodeHandlers.put(LetExpr.class, LetExprHandler.class);
		nodeHandlers.put(TypeBoundKind.class, TypeBoundKindHandler.class);

	}

	private static class PositionImpl implements Position {

		private final int line;
		private final int column;

		private PositionImpl(int line, int column) {
			this.line = line;
			this.column = column;
		}

		@Override
		public int getColumnNumber() {
			return column;
		}

		@Override
		public int getLineNumber() {
			return line;
		}

		public static Position createPosition(LineMap lineMap, int position) {
			if (position < 0) {
				return new PositionImpl(-1, -1);
			}
			return new PositionImpl(lineMap.getLineNumber(position), lineMap
					.getColumnNumber(position));
		}

	}

}
