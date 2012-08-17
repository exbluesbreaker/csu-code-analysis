package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCEnhancedForLoop;

public class JCEnhancedForLoopHandler extends JCTreeHandler {

    public JCEnhancedForLoopHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCEnhancedForLoop loop = JCEnhancedForLoop.class.cast(node);
        walker.handle(loop.var, "nodename.variable");
        walker.handle(loop.expr, "nodename.expression");
        walker.handle(loop.body, "nodename.body");
    }

}
