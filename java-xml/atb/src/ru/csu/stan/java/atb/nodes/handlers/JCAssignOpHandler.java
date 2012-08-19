package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCAssignOp;

public class JCAssignOpHandler extends JCTreeHandler {

    public JCAssignOpHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCAssignOp asOp = JCAssignOp.class.cast(node);
        walker.handle(asOp.lhs, "nodename.left_part");
        walker.handle(asOp.rhs, "nodename.right_part");
        walker.handle(asOp.operator, "nodename.operator");
    }

}
