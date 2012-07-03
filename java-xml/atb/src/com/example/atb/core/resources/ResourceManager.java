package com.example.atb.core.resources;

import java.util.MissingResourceException;
import java.util.ResourceBundle;

public class ResourceManager {

    private static ResourceBundle bundle;

    private static ResourceBundle getBundle() {
        if (bundle == null) {
            bundle = ResourceBundle.getBundle(ResourceManager.class.getPackage().getName()
                    + ".resources"); // $NON-NLS$
        }
        return bundle;
    }

    public static String getResourceString(String key) {
        try {
            return getBundle().getString(key);
        } catch (MissingResourceException e) {
            return key;
        }
    }
}
