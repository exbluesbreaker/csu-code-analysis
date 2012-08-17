package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCThrow;

public class JCThrowHandler extends JCTreeHandler {

    public JCThrowHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCThrow thr = JCThrow.class.cast(node);
        walker.handle(thr.expr, "nodename.expression");
    }

}
