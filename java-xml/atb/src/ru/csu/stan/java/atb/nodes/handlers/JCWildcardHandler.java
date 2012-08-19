package ru.csu.stan.java.atb.nodes.handlers;

import ru.csu.stan.java.atb.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCWildcard;

public class JCWildcardHandler extends JCTreeHandler {

    public JCWildcardHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCWildcard wildCard = JCWildcard.class.cast(node);
        // в этом нет необходимости, сам wildcard возвращает свой внутренний тип
//        walker.handle(wildCard.kind, "nodename.kind");
        walker.handle(wildCard.inner, "nodename.inner");
    }

}
