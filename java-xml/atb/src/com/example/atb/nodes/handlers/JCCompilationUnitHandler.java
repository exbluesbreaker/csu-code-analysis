package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCCompilationUnit;

public class JCCompilationUnitHandler extends JCTreeHandler {

    public JCCompilationUnitHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    public void execute(JCTree node) {
        JCCompilationUnit compUnit = JCCompilationUnit.class.cast(node);
        walker.handle(compUnit.packageAnnotations, "nodename.package_annotations");
        walker.handle(compUnit.pid, "nodename.package_identifier");
        walker.handle(compUnit.defs, "nodename.definitions");
        walker.handle(compUnit.packge, "nodename.package");
        walker.handleFlags(compUnit.flags);
    }

}
