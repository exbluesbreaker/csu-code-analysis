package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

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
        walker.handle(assign.rhs, "nodename.right_part");
    }

}
