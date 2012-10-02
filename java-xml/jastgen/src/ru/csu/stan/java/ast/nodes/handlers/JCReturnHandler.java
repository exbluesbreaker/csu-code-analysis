package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCReturn;

public class JCReturnHandler extends JCTreeHandler {

    public JCReturnHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCReturn ret = JCReturn.class.cast(node);
        walker.handle(ret.expr, "nodename.expression");
    }

}
