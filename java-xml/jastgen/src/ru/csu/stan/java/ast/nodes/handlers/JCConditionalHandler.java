package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCConditional;

public class JCConditionalHandler extends JCTreeHandler {

    public JCConditionalHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCConditional cond = JCConditional.class.cast(node);
        walker.handle(cond.cond, "nodename.condition");
        walker.handle(cond.truepart, "nodename.true_part");
        walker.handle(cond.falsepart, "nodename.false_part");
    }

}
