package ru.csu.stan.java.classgen.util;

enum ContextState {
	EMPTY,
	COMPILATION_UNIT,
	IMPORT,
	PACKAGE,
	CLASS,
	NEW_CLASS,
	FIELD,
	METHOD,
	ARGUMENT,
	PARENT,
	MODIFIERS,
	RETURN_TYPE,
	FIELD_TYPE,
	ARG_TYPE

}
