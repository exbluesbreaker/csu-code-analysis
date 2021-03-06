package ru.csu.stan.java.ast.nodes.handlers;

import ru.csu.stan.java.ast.core.TreeWalker;

import com.sun.tools.javac.tree.JCTree;
import com.sun.tools.javac.tree.JCTree.JCAnnotation;

public class JCAnnotationHandler extends JCTreeHandler {

    public JCAnnotationHandler(TreeWalker walker) {
        super(walker);
    }

    @Override
    protected void execute(JCTree node) {
        JCAnnotation annotation = JCAnnotation.class.cast(node);
        walker.handle(annotation.annotationType, "nodename.annotation_type");
        walker.handle(annotation.args, "nodename.arguments");
    }

}
