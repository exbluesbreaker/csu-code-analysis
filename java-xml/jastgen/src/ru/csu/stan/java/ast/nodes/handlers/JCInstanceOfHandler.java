package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCInstanceOf;

public class JCInstanceOfHandler extends JCTreeHandler {

    public JCInstanceOfHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCInstanceOf iOf = JCInstanceOf.class.cast(node);
        walker.handle(iOf.expr, "nodename.expression");
        walker.handle(iOf.clazz, "nodename.class");
    }

}
