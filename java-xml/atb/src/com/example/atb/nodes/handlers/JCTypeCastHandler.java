package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCTypeCast;

public class JCTypeCastHandler extends JCTreeHandler {

    public JCTypeCastHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCTypeCast cast = JCTypeCast.class.cast(node);
        walker.handle(cast.clazz, "nodename.class");
        walker.handle(cast.expr, "nodename.expression");
    }

}
