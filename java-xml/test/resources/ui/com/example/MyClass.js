if (typeof sourceFiles.com == undefined)
  sourceFiles.com = {};

if (typeof sourceFiles.com.example == undefined)
  sourceFiles.com.example = {};

sourceFiles.com.example.MyClass = function(){
  return "package com.example;\n\
\n\
import java.util.ArrayList;\n\
import java.util.Collection;\n\
import java.util.Iterator;\n\
import java.util.List;\n\
import java.util.ListIterator;\n\
\n\
public class <a name=\"1\">MyClass</a> extends ArrayList<Object>{\n\
    \n\
    public final static String <a name=\"1.0\">A</a> = \"asdasd\";\n\
    private StringBuffer <a name=\"1.1\">sb</a> = new StringBuffer();\n\
    private int <a name=\"1.2\">x</a> = Integer.valueOf(sb.toString());\n\
    OurClass<IAction> <a name=\"1.3\">list</a>;\n\
    List<IAction> <a name=\"1.4\">actionList</a>;\n\
    \n\
    public static void <a name=\"1.0\">main</a>(IAction <a name=\"1.0.0\">action</a>) {\n\
        System.out.println(MyClass.A);\n\
        List<Object> a = new List<Object>() <a name=\"2\">{</a>\n\
			\n\
			@Override\n\
			public <T> T[] <a name=\"2.0\">toArray</a>(T[] <a name=\"2.0.0\">a</a>) {\n\
				// TODO Auto-generated method stub\n\
				return null;\n\
			}\n\
			\n\
			@Override\n\
			public Object[] <a name=\"2.1\">toArray</a>() {\n\
				// TODO Auto-generated method stub\n\
				return null;\n\
			}\n\
			\n\
			@Override\n\
			public List<Object> <a name=\"2.2\">subList</a>(int <a name=\"2.2.0\">fromIndex</a>, int <a name=\"2.2.1\">toIndex</a>) {\n\
				// TODO Auto-generated method stub\n\
				return null;\n\
			}\n\
			\n\
			@Override\n\
			public int <a name=\"2.3\">size</a>() {\n\
				// TODO Auto-generated method stub\n\
				return 0;\n\
			}\n\
			\n\
			@Override\n\
			public Object <a name=\"2.4\">set</a>(int <a name=\"2.4.0\">index</a>, Object <a name=\"2.4.1\">element</a>) {\n\
				// TODO Auto-generated method stub\n\
				return null;\n\
			}\n\
			\n\
			@Override\n\
			public boolean <a name=\"2.5\">retainAll</a>(Collection<?> <a name=\"2.5.0\">c</a>) {\n\
				// TODO Auto-generated method stub\n\
				return false;\n\
			}\n\
			\n\
			@Override\n\
			public boolean <a name=\"2.6\">removeAll</a>(Collection<?> <a name=\"2.6.0\">c</a>) {\n\
				// TODO Auto-generated method stub\n\
				return false;\n\
			}\n\
			\n\
			@Override\n\
			public Object <a name=\"2.7\">remove</a>(int <a name=\"2.7.0\">index</a>) {\n\
				// TODO Auto-generated method stub\n\
				return null;\n\
			}\n\
			\n\
			@Override\n\
			public boolean <a name=\"2.8\">remove</a>(Object <a name=\"2.8.0\">o</a>) {\n\
				// TODO Auto-generated method stub\n\
				return false;\n\
			}\n\
			\n\
			@Override\n\
			public ListIterator<Object> <a name=\"2.9\">listIterator</a>(int <a name=\"2.9.0\">index</a>) {\n\
				// TODO Auto-generated method stub\n\
				return null;\n\
			}\n\
			\n\
			@Override\n\
			public ListIterator<Object> <a name=\"2.10\">listIterator</a>() {\n\
				// TODO Auto-generated method stub\n\
				return null;\n\
			}\n\
			\n\
			@Override\n\
			public int <a name=\"2.11\">lastIndexOf</a>(Object <a name=\"2.11.0\">o</a>) {\n\
				// TODO Auto-generated method stub\n\
				return 0;\n\
			}\n\
			\n\
			@Override\n\
			public Iterator<Object> <a name=\"2.12\">iterator</a>() {\n\
				// TODO Auto-generated method stub\n\
				return null;\n\
			}\n\
			\n\
			@Override\n\
			public boolean <a name=\"2.13\">isEmpty</a>() {\n\
				// TODO Auto-generated method stub\n\
				return false;\n\
			}\n\
			\n\
			@Override\n\
			public int <a name=\"2.14\">indexOf</a>(Object <a name=\"2.14.0\">o</a>) {\n\
				// TODO Auto-generated method stub\n\
				return 0;\n\
			}\n\
			\n\
			@Override\n\
			public Object <a name=\"2.15\">get</a>(int <a name=\"2.15.0\">index</a>) {\n\
				// TODO Auto-generated method stub\n\
				return null;\n\
			}\n\
			\n\
			@Override\n\
			public boolean <a name=\"2.16\">containsAll</a>(Collection<?> <a name=\"2.16.0\">c</a>) {\n\
				// TODO Auto-generated method stub\n\
				return false;\n\
			}\n\
			\n\
			@Override\n\
			public boolean <a name=\"2.17\">contains</a>(Object <a name=\"2.17.0\">o</a>) {\n\
				// TODO Auto-generated method stub\n\
				return false;\n\
			}\n\
			\n\
			@Override\n\
			public void <a name=\"2.18\">clear</a>() {\n\
				// TODO Auto-generated method stub\n\
				\n\
			}\n\
			\n\
			@Override\n\
			public boolean <a name=\"2.19\">addAll</a>(int <a name=\"2.19.0\">index</a>, Collection<? extends Object> <a name=\"2.19.1\">c</a>) {\n\
				// TODO Auto-generated method stub\n\
				return false;\n\
			}\n\
			\n\
			@Override\n\
			public boolean <a name=\"2.20\">addAll</a>(Collection<? extends Object> <a name=\"2.20.0\">c</a>) {\n\
				// TODO Auto-generated method stub\n\
				return false;\n\
			}\n\
			\n\
			@Override\n\
			public void <a name=\"2.21\">add</a>(int <a name=\"2.21.0\">index</a>, Object <a name=\"2.21.1\">element</a>) {\n\
				// TODO Auto-generated method stub\n\
				\n\
			}\n\
			\n\
			@Override\n\
			public boolean <a name=\"2.22\">add</a>(Object <a name=\"2.22.0\">e</a>) {\n\
				// TODO Auto-generated method stub\n\
				return false;\n\
			}\n\
		};\n\
    }\n\
    \n\
    public OurClass.MyClass2 <a name=\"1.1\">bar</a>(String <a name=\"1.1.0\">a</a>, boolean <a name=\"1.1.1\">b</a>, OurClass.MyClass2 <a name=\"1.1.2\">c</a>){\n\
    	return null;\n\
    }\n\
    \n\
    private OurClass.MyClass2 <a name=\"1.5\">hoho</a>;\n\
    \n\
    public static class <a name=\"3\">MyClass2</a> {\n\
        \n\
        public void <a name=\"3.0\">foo</a>() {\n\
            System.out.println(MyClass.A);\n\
        }\n\
        \n\
        public static class <a name=\"4\">MyClass3</a> {}\n\
        \n\
    }\n\
    \n\
\n\
}\n\
";
}
