package ru.csu.stan.java.classgen.util;

enum ContextState {
	EMPTY,
	IMPORT,
	PACKAGE,
	CLASS,
	FIELD,
	METHOD,
	ARGUMENT,
	PARENT,
}
