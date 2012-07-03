package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCPrimitiveTypeTree;

public class JCPrimitiveTypeTreeHandler extends JCTreeHandler {

    public JCPrimitiveTypeTreeHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCPrimitiveTypeTree primitiveType = JCPrimitiveTypeTree.class.cast(node);
        walker.handlePrimitiveType(primitiveType.getPrimitiveTypeKind());
    }

}
