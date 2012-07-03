package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCBlock;

public class JCBlockHandler extends JCTreeHandler {

    public JCBlockHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCBlock block = JCBlock.class.cast(node);
        walker.handleFlags(block.flags);
        walker.handle(block.stats, "nodename.statements");
    }
}
