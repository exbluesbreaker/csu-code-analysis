package com.example.atb.main;

import java.io.File;
import java.io.FileFilter;
import java.io.FileNotFoundException;
import java.util.LinkedList;
import java.util.List;

public class JavaFileSearcher {

    public static List<File> getJavaFilesFromDirectory(String path) throws FileNotFoundException {
        File dir = new File(path);
        if (!dir.exists()) {
            throw new FileNotFoundException("No such directory.");
        } else if (dir.isFile()) {
            throw new FileNotFoundException("Given path is not directory.");
        }
        List<File> files = new LinkedList<File>();
        getFiles(dir.getAbsoluteFile(), files);
        return files;
    }

    private static List<File> getFiles(File rootDirectory, final List<File> javaFiles) {
        final List<File> dirs = new LinkedList<File>();
        File[] listFiles = rootDirectory.listFiles(new FileFilter() {
            @Override
            public boolean accept(File pathname) {
                if (pathname.isDirectory()) {
                    dirs.add(pathname);
                    return false;
                } else if (pathname.isFile() && pathname.getName().toLowerCase().endsWith(".java")) {
                    return true;
                }
                return false;
            }
        });
        for (File file : listFiles) {
            javaFiles.add(file);
        }
        for (File dir : dirs) {
            getFiles(dir, javaFiles);
        }
        return javaFiles;
    }

}
