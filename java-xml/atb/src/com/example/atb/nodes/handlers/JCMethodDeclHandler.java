package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCMethodDecl;

public class JCMethodDeclHandler extends JCTreeHandler {

    public JCMethodDeclHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCMethodDecl methodNode = JCMethodDecl.class.cast(node);
        walker.handle(methodNode.name, "nodename.name");
        walker.handle(methodNode.mods, "nodename.modifiers");
        walker.handle(methodNode.restype, "nodename.result_type");
        walker.handle(methodNode.typarams, "nodename.type_parameters");
        walker.handle(methodNode.params, "nodename.parameters");
        walker.handle(methodNode.thrown, "nodename.thrown");
        walker.handle(methodNode.body, "nodename.body");
        walker.handle(methodNode.defaultValue, "nodename.default_value");
        walker.handle(methodNode.sym, "nodename.symbol");
    }
}
