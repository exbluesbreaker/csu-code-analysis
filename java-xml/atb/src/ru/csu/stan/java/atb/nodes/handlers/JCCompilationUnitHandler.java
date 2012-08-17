package ru.csu.stan.java.atb.nodes.handlers;

import java.util.LinkedList;
import java.util.List;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCCompilationUnit;

public class JCCompilationUnitHandler extends JCTreeHandler {

    public JCCompilationUnitHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    public void execute(JCTree node) {
        JCCompilationUnit compUnit = JCCompilationUnit.class.cast(node);
        walker.handleFlags(compUnit.flags);
        walker.handle(compUnit.packageAnnotations, "nodename.package_annotations");
        List<JCTree> packageList = new LinkedList<JCTree>();
        if (compUnit.pid != null)
        	packageList.add(compUnit.pid);
        walker.handle(packageList, "package");
        walker.handle(compUnit.defs, "definitions");
        walker.handle(compUnit.packge, "nodename.package");
    }

}
