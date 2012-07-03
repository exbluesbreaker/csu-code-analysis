package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCSwitch;

public class JCSwitchHandler extends JCTreeHandler {

    public JCSwitchHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCSwitch switchStmt = JCSwitch.class.cast(node);
        walker.handle(switchStmt.selector, "nodename.selector");
        walker.handle(switchStmt.cases, "nodename.cases");
    }

}
