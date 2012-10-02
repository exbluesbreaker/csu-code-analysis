package ru.csu.stan.java.ast.symbols.handlers;

import ru.csu.stan.java.ast.main.TreeWalkerImpl;

import com.sun.tools.javac.code.Symbol;

public abstract class SymbolHandler<K extends Symbol> {
    
    protected final TreeWalkerImpl walker;
    protected final K symbol;
    
    public SymbolHandler(TreeWalkerImpl walker, K symbol) {
        this.walker = walker;
        this.symbol = symbol;
    }
    
    public final void perform() {
        execute();
    }
    
    protected abstract void execute();

}
