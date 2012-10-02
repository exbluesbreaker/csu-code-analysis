package ru.csu.stan.java.ast.core;

import java.text.MessageFormat;

public class BypassException extends Exception {

    private static final long serialVersionUID = -2224154321716848159L;

    public BypassException() {
    }

    public BypassException(String message) {
        super(message);
    }

    public BypassException(Throwable cause) {
        super(cause);
    }

    public BypassException(String message, Throwable cause) {
        super(message, cause);
    }

    public BypassException(String message, Object... arguments) {
        this(MessageFormat.format(message, arguments));
    }
    
    public BypassException(String message, Throwable cause, Object... arguments) {
        this(MessageFormat.format(message, arguments), cause);
    }

}
