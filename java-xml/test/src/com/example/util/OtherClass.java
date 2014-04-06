package com.example.util;

import ru.test.ITesting;

import com.example.IAction;
import com.example.MyClass;


public class OtherClass extends MyClass implements IAction, ITesting{
	
	public static class AnotherOtherClass extends MyClass2{
		private MyClass3 field;
		private MyClass2 field1;
		private ITesting field2;
		
		public static class AndNowSomethingCompletelyDifferent extends MyClass3{
		}
		
	}
	
	
}
