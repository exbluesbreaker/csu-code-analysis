package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCUnary;

public class JCUnaryHandler extends JCTreeHandler {

    public JCUnaryHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCUnary unary = JCUnary.class.cast(node);
        walker.handle(unary.arg, "nodename.argument");
        walker.handle(unary.operator, "nodename.argument");
    }

}
