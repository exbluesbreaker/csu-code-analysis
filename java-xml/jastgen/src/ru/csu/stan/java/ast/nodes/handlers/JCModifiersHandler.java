package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCModifiers;

public class JCModifiersHandler extends JCTreeHandler {

    public JCModifiersHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCModifiers mods = JCModifiers.class.cast(node);
        walker.handleFlags(mods.flags);
        walker.handle(mods.annotations, "nodename.annotations");
    }

}
