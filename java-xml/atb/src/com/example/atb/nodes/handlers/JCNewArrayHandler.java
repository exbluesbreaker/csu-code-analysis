package com.example.atb.nodes.handlers;

import com.example.atb.core.TreeWalker;
import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCNewArray;

public class JCNewArrayHandler extends JCTreeHandler {

    public JCNewArrayHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCNewArray array = JCNewArray.class.cast(node);
        walker.handle(array.elemtype, "nodename.type");
        walker.handle(array.dims, "nodename.dimensions");
        walker.handle(array.elems, "nodename.elements");
    }

}
