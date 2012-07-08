package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCCase;

public class JCCaseHandler extends JCTreeHandler {

    public JCCaseHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCCase cas = JCCase.class.cast(node);
        walker.handle(cas.pat, "nodename.pattern");
        walker.handle(cas.stats, "nodename.statements");
    }

}