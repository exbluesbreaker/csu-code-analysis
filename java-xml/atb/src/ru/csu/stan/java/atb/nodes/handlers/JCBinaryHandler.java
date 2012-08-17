package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCBinary;

public class JCBinaryHandler extends JCTreeHandler {

    public JCBinaryHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCBinary binary = JCBinary.class.cast(node);
        walker.handle(binary.lhs, "nodename.left_part");
        walker.handle(binary.rhs, "nodename.right_part");
        walker.handle(binary.operator, "nodename.operator");
    }

}
