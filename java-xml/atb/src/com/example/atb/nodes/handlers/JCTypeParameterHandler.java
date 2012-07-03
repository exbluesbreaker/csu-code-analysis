package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCTypeParameter;

public class JCTypeParameterHandler extends JCTreeHandler {

    public JCTypeParameterHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCTypeParameter tParam = JCTypeParameter.class.cast(node);
        walker.handle(tParam.name, "nodename.name");
        walker.handle(tParam.bounds, "nodename.bounds");
    }

}
