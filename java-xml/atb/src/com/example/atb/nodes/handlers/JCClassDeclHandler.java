package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCClassDecl;

public class JCClassDeclHandler extends JCTreeHandler {

    public JCClassDeclHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCClassDecl decl = JCClassDecl.class.cast(node);
        walker.handle(decl.name, "nodename.name");
        walker.handle(decl.mods, "nodename.modifiers");
        walker.handle(decl.typarams, "nodename.type_parameters");
        walker.handle(decl.extending, "nodename.extending");
        walker.handle(decl.implementing, "nodename.implementing");
        walker.handle(decl.defs, "nodename.definitions");
        walker.handle(decl.sym, "nodename.symbol");
    }
}
