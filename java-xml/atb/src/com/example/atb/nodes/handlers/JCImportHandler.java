package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCImport;

public class JCImportHandler extends JCTreeHandler {

    public JCImportHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCImport importNode = JCImport.class.cast(node);
        walker.handle(importNode.qualid, "nodename.qualifier");
    }

}