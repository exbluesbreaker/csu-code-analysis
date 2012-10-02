package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCAssert;

public class JCAssertHandler extends JCTreeHandler {

    public JCAssertHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCAssert asset = JCAssert.class.cast(node);
        walker.handle(asset.cond, "nodename.condition");
        walker.handle(asset.detail, "nodename.detail");
    }

}
