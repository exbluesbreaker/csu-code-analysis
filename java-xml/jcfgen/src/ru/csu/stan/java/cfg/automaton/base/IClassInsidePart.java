package ru.csu.stan.java.cfg.automaton.base;

import ru.csu.stan.java.cfg.util.scope.VariableScope;

public interface IClassInsidePart {
	String getClassName();
	int getNextInnerCount();
	VariableScope getVariableScope();
}
