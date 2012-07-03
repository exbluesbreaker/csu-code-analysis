package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;

public class JCLiteralHandler extends JCTreeHandler {

    public JCLiteralHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        // This Class is not usable any more.
    }

}
