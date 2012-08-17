package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCParens;

public class JCParensHandler extends JCTreeHandler {

    public JCParensHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCParens parent = JCParens.class.cast(node);
        walker.handle(parent.expr, "nodename.expression");
    }

}
