package com.example.atb.nodes.handlers;

import java.util.LinkedList;
import java.util.List;

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
        // generics
        walker.handle(decl.typarams, "generics");
        List<JCTree> extendsList = new LinkedList<JCTree>();
        if (decl.extending != null)
        	extendsList.add(decl.extending);
        walker.handle(extendsList, "extends");
        walker.handle(decl.implementing, "implements");
        walker.handle(decl.defs, "body");
        walker.handle(decl.sym, "nodename.symbol");
    }
}
