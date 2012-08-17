package ru.csu.stan.java.atb.nodes.handlers;

import java.util.LinkedList;
import java.util.List;

import ru.csu.stan.java.atb.core.TreeWalker;

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
        List<JCTree> resultTypeList = new LinkedList<JCTree>();
        if (methodNode.restype != null)
        	resultTypeList.add(methodNode.restype);
        walker.handle(resultTypeList, "resulttype");
        walker.handle(methodNode.typarams, "generics");
        walker.handle(methodNode.params, "parameters");
        walker.handle(methodNode.thrown, "thrown");
        walker.handle(methodNode.body, "nodename.body");
        walker.handle(methodNode.defaultValue, "nodename.default_value");
        walker.handle(methodNode.sym, "nodename.symbol");
    }
}
