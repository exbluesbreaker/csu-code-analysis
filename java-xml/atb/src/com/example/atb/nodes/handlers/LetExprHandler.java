package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.LetExpr;

public class LetExprHandler extends JCTreeHandler {

    public LetExprHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        LetExpr lExpr = LetExpr.class.cast(node);
        walker.handle(lExpr.defs, "nodename.definitions");
        walker.handle(lExpr.expr, "nodename.expression");
    }

}
