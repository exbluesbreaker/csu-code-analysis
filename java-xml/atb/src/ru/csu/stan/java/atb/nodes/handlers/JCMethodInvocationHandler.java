package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCMethodInvocation;

public class JCMethodInvocationHandler extends JCTreeHandler {

    public JCMethodInvocationHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCMethodInvocation meth = JCMethodInvocation.class.cast(node);
        walker.handle(meth.typeargs, "nodename.arguments_types");
        walker.handle(meth.meth, "nodename.method");
        walker.handle(meth.args, "nodename.arguments");
        walker.handle(meth.varargsElement, "nodename.vararg");
    }

}
