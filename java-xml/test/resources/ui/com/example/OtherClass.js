if (typeof sourceFiles.com == undefined)
  sourceFiles.com = {};

if (typeof sourceFiles.com.example == undefined)
  sourceFiles.com.example = {};

sourceFiles.com.example.OtherClass = function(){
  return "package com.example;\n\
\n\
\n\
public class <a name=\"8\">OtherClass</a> extends MyClass implements IAction {\n\
	\n\
	public static class <a name=\"9\">AnotherOtherClass</a> extends MyClass2{\n\
		private MyClass3 <a name=\"9.0\">field</a>;\n\
		\n\
		public static class <a name=\"10\">AndNowSomethingCompletelyDifferent</a> extends MyClass3{\n\
		}\n\
		\n\
	}\n\
	\n\
	\n\
}\n\
";
}
