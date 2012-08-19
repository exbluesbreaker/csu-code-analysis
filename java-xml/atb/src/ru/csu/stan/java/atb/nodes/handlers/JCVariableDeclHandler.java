package ru.csu.stan.java.atb.nodes.handlers;

import java.util.LinkedList;
import java.util.List;

import ru.csu.stan.java.atb.core.TreeWalker;

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
        List<JCTree> varTypeList = new LinkedList<JCTree>();
        if (decl.vartype != null)
        	varTypeList.add(decl.vartype);
        walker.handle(varTypeList, "vartype");
        List<JCTree> initList = new LinkedList<JCTree>();
        if (decl.init != null)
        	initList.add(decl.init);
        walker.handle(initList, "init");
    }

}
