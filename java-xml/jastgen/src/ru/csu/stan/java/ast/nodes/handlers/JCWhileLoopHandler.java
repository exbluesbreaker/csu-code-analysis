package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCWhileLoop;

public class JCWhileLoopHandler extends JCTreeHandler {

    public JCWhileLoopHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCWhileLoop loop = JCWhileLoop.class.cast(node);
        walker.handle(loop.body, "nodename.body");
        walker.handle(loop.cond, "nodename.condition");
    }

}
