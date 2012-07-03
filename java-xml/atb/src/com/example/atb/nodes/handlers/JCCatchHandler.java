package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCCatch;

public class JCCatchHandler extends JCTreeHandler {

    public JCCatchHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCCatch cat = JCCatch.class.cast(node);
        walker.handle(cat.param, "nodename.parameter");
        walker.handle(cat.body, "nodename.body");
    }

}
