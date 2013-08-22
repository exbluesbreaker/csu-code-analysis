if (typeof sourceFiles.com == undefined)
  sourceFiles.com = {};

if (typeof sourceFiles.com.example == undefined)
  sourceFiles.com.example = {};

if (typeof sourceFiles.com.example.util == undefined)
  sourceFiles.com.example.util = {};

sourceFiles.com.example.util.OtherClass = function(){
  return "package com.example.util;\n\
\n\
import com.example.IAction;\n\
import com.example.MyClass;\n\
\n\
\n\
public class <a name=\"11\">OtherClass</a> extends MyClass implements IAction {\n\
	\n\
	public static class <a name=\"12\">AnotherOtherClass</a> extends MyClass2{\n\
		private MyClass3 <a name=\"12.0\">field</a>;\n\
		\n\
		public static class <a name=\"13\">AndNowSomethingCompletelyDifferent</a> extends MyClass3{\n\
		}\n\
		\n\
	}\n\
	\n\
	\n\
}\n\
";
}
