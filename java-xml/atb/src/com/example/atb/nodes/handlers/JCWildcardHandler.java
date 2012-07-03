package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCWildcard;

public class JCWildcardHandler extends JCTreeHandler {

    public JCWildcardHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCWildcard wildCard = JCWildcard.class.cast(node);
        walker.handle(wildCard.kind, "nodename.kind");
        walker.handle(wildCard.inner, "nodename.inner");
    }

}
