package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCContinue;

public class JCContinueHandler extends JCTreeHandler {

    public JCContinueHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCContinue cont = JCContinue.class.cast(node);
        walker.handle(cont.label, "nodename.label");
        walker.handle(cont.target, "nodename.target");
    }

}