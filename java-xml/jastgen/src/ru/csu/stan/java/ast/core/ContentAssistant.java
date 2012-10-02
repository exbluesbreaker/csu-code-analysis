package ru.csu.stan.java.ast.core;

import java.util.HashMap;
import java.util.Map;

import javax.lang.model.type.TypeKind;

import ru.csu.stan.java.ast.core.resources.ResourceManager;

import com.sun.source.tree.Tree.Kind;

public class ContentAssistant {
    
    public static String getNodeName(String innerNodeName) {
        return ResourceManager.getResourceString(innerNodeName);
    }
    
    private static final Map<Kind, String> treeNodesNames = new HashMap<Kind, String>();

    static {
        treeNodesNames.put(Kind.ANNOTATION, "tags.annotation");
        treeNodesNames.put(Kind.ARRAY_ACCESS, "tags.array_access");
        treeNodesNames.put(Kind.ARRAY_TYPE, "tags.array_type");
        treeNodesNames.put(Kind.ASSERT, "tags.assert");
        treeNodesNames.put(Kind.ASSIGNMENT, "tags.assignment");
        treeNodesNames.put(Kind.BLOCK, "tags.block");
        treeNodesNames.put(Kind.BREAK, "tags.break");
        treeNodesNames.put(Kind.CASE, "tags.case");
        treeNodesNames.put(Kind.CATCH, "tags.catch");
        treeNodesNames.put(Kind.CLASS, "tags.class");
        treeNodesNames.put(Kind.COMPILATION_UNIT, "tags.compilation_unit");
        treeNodesNames.put(Kind.CONDITIONAL_EXPRESSION, "tags.conditional_expression");
        treeNodesNames.put(Kind.CONTINUE, "tags.continue");
        treeNodesNames.put(Kind.DO_WHILE_LOOP, "tags.do_while_loop");
        treeNodesNames.put(Kind.ENHANCED_FOR_LOOP, "tags.enhanced_for_loop");
        treeNodesNames.put(Kind.EXPRESSION_STATEMENT, "tags.expression_statement");
        treeNodesNames.put(Kind.MEMBER_SELECT, "tags.member_select");
        treeNodesNames.put(Kind.FOR_LOOP, "tags.for_loop");
        treeNodesNames.put(Kind.IDENTIFIER, "tags.identifier");
        treeNodesNames.put(Kind.IF, "tags.if");
        treeNodesNames.put(Kind.IMPORT, "tags.import");
        treeNodesNames.put(Kind.INSTANCE_OF, "tags.instance_of");
        treeNodesNames.put(Kind.LABELED_STATEMENT, "tags.labeled_statement");
        treeNodesNames.put(Kind.METHOD, "tags.method");
        treeNodesNames.put(Kind.METHOD_INVOCATION, "method_invocation");
        treeNodesNames.put(Kind.MODIFIERS, "tags.modifiers");
        treeNodesNames.put(Kind.NEW_ARRAY, "tags.new_array");
        treeNodesNames.put(Kind.NEW_CLASS, "tags.new_class");
        treeNodesNames.put(Kind.PARENTHESIZED, "tags.parenthesized");
        treeNodesNames.put(Kind.PRIMITIVE_TYPE, "tags.primitive_type");
        treeNodesNames.put(Kind.RETURN, "tags.return");
        treeNodesNames.put(Kind.EMPTY_STATEMENT, "tags.empty_statement");
        treeNodesNames.put(Kind.SWITCH, "tags.switch");
        treeNodesNames.put(Kind.SYNCHRONIZED, "tags.synchronized");
        treeNodesNames.put(Kind.THROW, "tags.throw");
        treeNodesNames.put(Kind.TRY, "tags.try");
        treeNodesNames.put(Kind.PARAMETERIZED_TYPE, "tags.parameterized_type");
        treeNodesNames.put(Kind.TYPE_CAST, "tags.type_cast");
        treeNodesNames.put(Kind.TYPE_PARAMETER, "tags.type_parameter");
        treeNodesNames.put(Kind.VARIABLE, "tags.variable");
        treeNodesNames.put(Kind.WHILE_LOOP, "tags.while_loop");
        treeNodesNames.put(Kind.POSTFIX_INCREMENT, "tags.postfix_increment");
        treeNodesNames.put(Kind.POSTFIX_DECREMENT, "tags.postfic_decrement");
        treeNodesNames.put(Kind.PREFIX_INCREMENT, "tags.prefix_increment");
        treeNodesNames.put(Kind.PREFIX_DECREMENT, "tags.prefix_decrement");
        treeNodesNames.put(Kind.UNARY_PLUS, "tags.unary_plus");
        treeNodesNames.put(Kind.UNARY_MINUS, "tags.unary_minus");
        treeNodesNames.put(Kind.BITWISE_COMPLEMENT, "tags.bitwise_complement");
        treeNodesNames.put(Kind.LOGICAL_COMPLEMENT, "tags.logical_complement");
        treeNodesNames.put(Kind.MULTIPLY, "tags.multiply");
        treeNodesNames.put(Kind.DIVIDE, "tags.divide");
        treeNodesNames.put(Kind.REMAINDER, "tags.remainder");
        treeNodesNames.put(Kind.PLUS, "tags.plus");
        treeNodesNames.put(Kind.MINUS, "tags.minus");
        treeNodesNames.put(Kind.LEFT_SHIFT, "tags.left_shift");
        treeNodesNames.put(Kind.RIGHT_SHIFT, "tags.right_shift");
        treeNodesNames.put(Kind.UNSIGNED_RIGHT_SHIFT, "tags.unsigned_right_shift");
        treeNodesNames.put(Kind.LESS_THAN, "tags.less_than");
        treeNodesNames.put(Kind.GREATER_THAN, "tags.grater_than");
        treeNodesNames.put(Kind.LESS_THAN_EQUAL, "tags.less_than_equal");
        treeNodesNames.put(Kind.GREATER_THAN_EQUAL, "tags.greater_than_equal");
        treeNodesNames.put(Kind.EQUAL_TO, "tags.equal_to");
        treeNodesNames.put(Kind.NOT_EQUAL_TO, "tags.not_equal_to");
        treeNodesNames.put(Kind.AND, "tags.and");
        treeNodesNames.put(Kind.XOR, "tags.xor");
        treeNodesNames.put(Kind.OR, "tags.or");
        treeNodesNames.put(Kind.CONDITIONAL_AND, "tags.conditional_end");
        treeNodesNames.put(Kind.CONDITIONAL_OR, "tags.conditional_or");
        treeNodesNames.put(Kind.MULTIPLY_ASSIGNMENT, "tags.multiply_assignment");
        treeNodesNames.put(Kind.DIVIDE_ASSIGNMENT, "tags.divide_assignment");
        treeNodesNames.put(Kind.REMAINDER_ASSIGNMENT, "tags.remainder_assignment");
        treeNodesNames.put(Kind.PLUS_ASSIGNMENT, "tags.plus_assignment");
        treeNodesNames.put(Kind.MINUS_ASSIGNMENT, "tags.minus_assignment");
        treeNodesNames.put(Kind.LEFT_SHIFT_ASSIGNMENT, "tags.left_shift_assignment");
        treeNodesNames.put(Kind.RIGHT_SHIFT_ASSIGNMENT, "tags.right_shift_assignment");
        treeNodesNames.put(Kind.UNSIGNED_RIGHT_SHIFT_ASSIGNMENT,
                "tags.unsigned_right_shift_assignment");
        treeNodesNames.put(Kind.AND_ASSIGNMENT, "tags.and_assignment");
        treeNodesNames.put(Kind.XOR_ASSIGNMENT, "tags.xor_assignment");
        treeNodesNames.put(Kind.OR_ASSIGNMENT, "tags.or_assignment");
        treeNodesNames.put(Kind.INT_LITERAL, "tags.int_literal");
        treeNodesNames.put(Kind.LONG_LITERAL, "tags.long_literal");
        treeNodesNames.put(Kind.FLOAT_LITERAL, "float_literal");
        treeNodesNames.put(Kind.DOUBLE_LITERAL, "tags.double_literal");
        treeNodesNames.put(Kind.BOOLEAN_LITERAL, "tags.boolean_literal");
        treeNodesNames.put(Kind.CHAR_LITERAL, "tags.char_literal");
        treeNodesNames.put(Kind.STRING_LITERAL, "tags.string_literal");
        treeNodesNames.put(Kind.NULL_LITERAL, "tags.null_literal");
        treeNodesNames.put(Kind.UNBOUNDED_WILDCARD, "tags.unbounded_wildcard");
        treeNodesNames.put(Kind.EXTENDS_WILDCARD, "tags.extends_wildcard");
        treeNodesNames.put(Kind.SUPER_WILDCARD, "tags.super_wildcard");
        treeNodesNames.put(Kind.ERRONEOUS, "tags.erroneous");
        treeNodesNames.put(Kind.OTHER, "tags.other");
    }

    public static String getTagNameByTreeElementKind(Kind kind) {
        return ResourceManager.getResourceString(treeNodesNames.get(kind));
    }

    private static final Map<TypeKind, String> typeKindNames = new HashMap<TypeKind, String>();

    static {
        typeKindNames.put(TypeKind.ARRAY, "typekind.array");
        typeKindNames.put(TypeKind.BOOLEAN, "typekind.boolean");
        typeKindNames.put(TypeKind.BYTE, "typekind.byte");
        typeKindNames.put(TypeKind.CHAR, "typekind.char");
        typeKindNames.put(TypeKind.DECLARED, "typekind.declared");
        typeKindNames.put(TypeKind.DOUBLE, "typekind.double");
        typeKindNames.put(TypeKind.ERROR, "typekind.error");
        typeKindNames.put(TypeKind.EXECUTABLE, "typekind.executable");
        typeKindNames.put(TypeKind.FLOAT, "typekind.float");
        typeKindNames.put(TypeKind.INT, "typekind.int");
        typeKindNames.put(TypeKind.LONG, "typekind.long");
        typeKindNames.put(TypeKind.NONE, "typekind.none");
        typeKindNames.put(TypeKind.NULL, "typekind.null");
        typeKindNames.put(TypeKind.OTHER, "typekind.other");
        typeKindNames.put(TypeKind.PACKAGE, "typekind.package");
        typeKindNames.put(TypeKind.SHORT, "typekind.short");
        typeKindNames.put(TypeKind.TYPEVAR, "typekind.typevar");
        typeKindNames.put(TypeKind.VOID, "typekind.void");
        typeKindNames.put(TypeKind.WILDCARD, "typekind.wildcard");
    }

    public static String getTypeKindToString(TypeKind typeKind) {
        return ResourceManager.getResourceString(typeKindNames.get(typeKind));
    }

}
