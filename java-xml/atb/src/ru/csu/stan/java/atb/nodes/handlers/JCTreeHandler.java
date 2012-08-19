package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;

public abstract class JCTreeHandler {

    protected final TreeWalker walker;

    public JCTreeHandler(TreeWalker walker) {
        this.walker = walker;
    }

    public final void perform(JCTree node) {
        execute(node);
    }

    protected abstract void execute(JCTree node);

}
