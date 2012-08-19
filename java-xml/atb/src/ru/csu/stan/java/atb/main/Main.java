package ru.csu.stan.java.atb.main;

import java.io.FileNotFoundException;

import javax.tools.JavaFileObject;

import ru.csu.stan.java.atb.core.BypassException;
import ru.csu.stan.java.atb.core.TraversalHandler;

import com.sun.tools.javac.file.JavacFileManager;
import com.sun.tools.javac.main.JavaCompiler;
import com.sun.tools.javac.tree.JCTree.JCCompilationUnit;
import com.sun.tools.javac.util.Context;

/**
 * "Главный класс" получения представления AST.
 * 
 */
public class Main {

	private Iterable<? extends JavaFileObject> units;
	private final Context context = new Context();
	private JavaCompiler compiler;
	
	/**
	 * Закрытый конструктор
	 */
	private Main() {}

	/**
	 * Статический метод генерации
	 */
	public static Main getInstance(String path) throws FileNotFoundException {
		Main main = new Main();
		main.fillUnits(path);
		main.compiler = new JavaCompiler(main.context);
		return main;
	}

	private void fillUnits(String path) throws FileNotFoundException {
		JavacFileManager jfm = new JavacFileManager(context, true, null);
		this.units = jfm.getJavaFileObjectsFromFiles(JavaFileSearcher
				.getJavaFilesFromDirectory(path));
	}

	public Iterable<? extends JavaFileObject> getUnits() {
		return units;
	}

	public void execute(JavaFileObject file,
			Iterable<TraversalHandler> handlers) throws BypassException {
		if (file == null) {
			throw new NullPointerException("File is null");
		}
		JCCompilationUnit unit = compiler.parse(file);
		TreeWalkerImpl treeWalker = new TreeWalkerImpl(unit, unit.lineMap);
		if (handlers != null) {
			for (TraversalHandler handler : handlers) {
				treeWalker.addBypassHandler(handler);
			}
		}
		treeWalker.executeBypass();
	}

}
