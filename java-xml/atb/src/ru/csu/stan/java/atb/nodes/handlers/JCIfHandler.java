package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCIf;

public class JCIfHandler extends JCTreeHandler {

    public JCIfHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCIf ifStmt = JCIf.class.cast(node);
        walker.handle(ifStmt.cond, "nodename.condition");
        walker.handle(ifStmt.thenpart, "nodename.then_part");
        walker.handle(ifStmt.elsepart, "nodename.else_part");
    }

}
