package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCExpressionStatement;

public class JCExpressionStatementHandler extends JCTreeHandler {

    public JCExpressionStatementHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCExpressionStatement expr = JCExpressionStatement.class.cast(node);
        walker.handle(expr.expr, "nodename.expression_statement");
    }

}
