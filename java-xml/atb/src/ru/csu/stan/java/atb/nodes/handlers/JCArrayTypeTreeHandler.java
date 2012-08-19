package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCArrayTypeTree;

public class JCArrayTypeTreeHandler extends JCTreeHandler {

    public JCArrayTypeTreeHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCArrayTypeTree att = JCArrayTypeTree.class.cast(node);
        walker.handle(att.elemtype, "nodename.array_type");
    }

}
