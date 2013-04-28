package com.example.util;

import com.example.IAction;
import com.example.MyClass;

public class OtherClass extends MyClass implements IAction {
	
	public static class AnotherOtherClass extends MyClass2{
		private MyClass3 field;
		
		public static class AndNowSomethingCompletelyDifferent extends MyClass3{
		}
		
	}
	
	
}
