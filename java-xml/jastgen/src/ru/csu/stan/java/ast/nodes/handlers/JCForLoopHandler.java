package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCForLoop;

public class JCForLoopHandler extends JCTreeHandler {

    public JCForLoopHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCForLoop loop = JCForLoop.class.cast(node);
        walker.handle(loop.init, "nodename.initialize_section");
        walker.handle(loop.cond, "nodename.condition_section");
        walker.handle(loop.step, "nodename.step_section");
        walker.handle(loop.body, "nodename.body");
    }

}
