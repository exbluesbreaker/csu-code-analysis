package com.example;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.ListIterator;

public class MyClass extends ArrayList<Object>{
    
    public final static String A = "asdasd";
    private StringBuffer sb = new StringBuffer();
    private int x = Integer.valueOf(sb.toString());
    OurClass<IAction> list;
    static java.util.List<IAction> actionList;
    
    public static void main(IAction action) {
        System.out.println(MyClass.A);
        actionList.add(null);
        int y = 0;
        try
        {
	        if (1+2 > 2+3)
	        	System.out.println("123");
	        else
	        	return;
        }
        catch (Exception e){
        	throw new RuntimeException();
        }
        finally{
        	System.out.println("aaaaaa");
        }
        
        for (int i = 0; i < 10; i++)
        	if (2>3)
        		System.out.println("2>3!");
        
        if (action.equals(A))
        	if (2 > 3)
        		System.out.println("000");
        	else{
        		System.out.println("1");
        		System.out.println("1");
        	}
        for (int i = 0; i < 10; i++){
        	System.out.println(123);
        	if (i > 5)
        		System.out.println(123);
        	else
        		System.out.println(123);
        }
        
        for (IAction act: actionList){
        	System.out.println(act.toString());
        }
        boolean x = false;
        	
        while (!x){
        	x = true;
        }
        
        while (x)
        	x = false;
        
        do
        	x = true;
        while (!x);
        
        do{
        	x = false;	
        }
        while (x);

    }
    
    public OurClass.MyClass2 bar(String a, boolean b, OurClass.MyClass2 c){
    	bar();
    	this.bar();
    	this.getValue().bar();
    	this.intValue.getValue();
    	this.intValue.intValue.getValue();
    	MyClass x = new MyClass();
    	return null;
    }
    
    public MyClass getValue(){
    	return this;
    }
    
    private MyClass intValue = this;
    
    public String bar() {
    	String s = "";
    	sb.append(s.toString());
    	MyClass2 mc2 = new MyClass2();
    	mc2.foo();
    	return sb.toString();
    }
    
    private OurClass.MyClass2 hoho;
    
    public static class MyClass2 {
        
        public void foo() {
            System.out.println(MyClass.A);
        }
        
        public static class MyClass3 {}
        
    }
    

}
