package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCNewClass;

public class JCNewClassHandler extends JCTreeHandler {

    public JCNewClassHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCNewClass nClass = JCNewClass.class.cast(node);
        walker.handle(nClass.encl, "nodename.enclosure");
        walker.handle(nClass.typeargs, "nodename.arguments_types");
        walker.handle(nClass.clazz, "nodename.class");
        walker.handle(nClass.args, "nodename.arguments");
        walker.handle(nClass.def, "nodename.definition");
        walker.handle(nClass.constructor, "nodename.constructor");
        walker.handle(nClass.varargsElement, "nodename.varargs");
    }

}
