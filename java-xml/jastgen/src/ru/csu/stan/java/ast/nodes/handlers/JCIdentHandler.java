package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCIdent;

public class JCIdentHandler extends JCTreeHandler {

    public JCIdentHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCIdent ident = JCIdent.class.cast(node);
        walker.handle(ident.name, "nodename.name");
        walker.handle(ident.sym, "nodename.symbol");
    }

}
