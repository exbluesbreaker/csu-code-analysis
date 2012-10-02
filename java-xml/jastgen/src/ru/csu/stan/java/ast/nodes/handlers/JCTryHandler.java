package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCTry;

public class JCTryHandler extends JCTreeHandler {

    public JCTryHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCTry tryStmt = JCTry.class.cast(node);
        walker.handle(tryStmt.body, "nodename.body");
        walker.handle(tryStmt.catchers, "nodename.catchers");
        walker.handle(tryStmt.finalizer, "nodename.finalizer");
    }

}
