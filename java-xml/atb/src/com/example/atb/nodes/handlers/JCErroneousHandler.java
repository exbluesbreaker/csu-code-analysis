package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCErroneous;

public class JCErroneousHandler extends JCTreeHandler {

    public JCErroneousHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCErroneous err = JCErroneous.class.cast(node);
        walker.handle(err.errs, "nodename.erroneous");
    }

}
