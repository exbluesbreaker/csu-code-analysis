package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCBreak;

public class JCBreakHandler extends JCTreeHandler {

    public JCBreakHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCBreak brk = JCBreak.class.cast(node);
        walker.handle(brk.label, "nodename.label");
        walker.handle(brk.target, "nodename.target");
    }

}
