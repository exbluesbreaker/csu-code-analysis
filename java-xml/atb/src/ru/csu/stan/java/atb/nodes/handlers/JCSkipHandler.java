package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;

public class JCSkipHandler extends JCTreeHandler {

    public JCSkipHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
     // This Class is not usable any more.
    }

}
