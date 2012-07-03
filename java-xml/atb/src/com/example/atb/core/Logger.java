package com.example.atb.core;

import java.util.logging.ConsoleHandler;

public class Logger extends java.util.logging.Logger {

    private static final String DEFAULT_LOGGER_NAME = "ATB Logger";

    protected Logger(String name, String resourceBundleName) {
        super(name, resourceBundleName);
    }

    private final static Logger defaultLogger = new Logger(DEFAULT_LOGGER_NAME, null);

    static {
        defaultLogger.addHandler(new ConsoleHandler());
    }

    public static Logger getLogger() {
        return defaultLogger;
    }

}
