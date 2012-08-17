package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCTypeApply;

public class JCTypeApplyHandler extends JCTreeHandler {

    public JCTypeApplyHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCTypeApply tApply = JCTypeApply.class.cast(node);
        walker.handle(tApply.clazz, "nodename.class");
        walker.handle(tApply.arguments, "nodename.arguments");
    }

}
