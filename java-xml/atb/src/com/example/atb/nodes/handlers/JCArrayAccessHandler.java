package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCArrayAccess;

public class JCArrayAccessHandler extends JCTreeHandler {

    public JCArrayAccessHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCArrayAccess aa = JCArrayAccess.class.cast(node);
        walker.handle(aa.index, "nodename.index");
        walker.handle(aa.indexed, "nodename.indexed");
    }

}
