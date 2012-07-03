package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCAssign;

public class JCAssignHandler extends JCTreeHandler {

    public JCAssignHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCAssign assign = JCAssign.class.cast(node);
        walker.handle(assign.lhs, "nodename.left_part");
        walker.handle(assign.lhs, "nodename.right_part");
    }

}
