package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCVariableDecl;

public class JCVariableDeclHandler extends JCTreeHandler {

    public JCVariableDeclHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCVariableDecl decl = JCVariableDecl.class.cast(node);
        walker.handle(decl.name, "nodename.name");
        walker.handle(decl.mods, "nodename.modifiers");
        walker.handle(decl.vartype, "nodename.type");
        walker.handle(decl.init, "nodename.init");
    }

}
