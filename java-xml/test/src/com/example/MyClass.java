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
    List<IAction> actionList;
    
    public static void main(IAction action) {
        System.out.println(MyClass.A);
        
        if (1+2 > 2+3)
        	System.out.println("123");
        else
        	System.out.println("321");
        
        if (action.equals(A))
        	if (2 > 3)
        		System.out.println("000");
        	else{
        		System.out.println("1");
        		System.out.println("1");
        	}
        
        List<Object> a = new List<Object>() {
			
			@Override
			public <T> T[] toArray(T[] a) {
				// TODO Auto-generated method stub
				return null;
			}
			
			@Override
			public Object[] toArray() {
				// TODO Auto-generated method stub
				return null;
			}
			
			@Override
			public List<Object> subList(int fromIndex, int toIndex) {
				// TODO Auto-generated method stub
				return null;
			}
			
			@Override
			public int size() {
				// TODO Auto-generated method stub
				return 0;
			}
			
			@Override
			public Object set(int index, Object element) {
				// TODO Auto-generated method stub
				return null;
			}
			
			@Override
			public boolean retainAll(Collection<?> c) {
				// TODO Auto-generated method stub
				return false;
			}
			
			@Override
			public boolean removeAll(Collection<?> c) {
				// TODO Auto-generated method stub
				return false;
			}
			
			@Override
			public Object remove(int index) {
				// TODO Auto-generated method stub
				return null;
			}
			
			@Override
			public boolean remove(Object o) {
				// TODO Auto-generated method stub
				return false;
			}
			
			@Override
			public ListIterator<Object> listIterator(int index) {
				// TODO Auto-generated method stub
				return null;
			}
			
			@Override
			public ListIterator<Object> listIterator() {
				// TODO Auto-generated method stub
				return null;
			}
			
			@Override
			public int lastIndexOf(Object o) {
				// TODO Auto-generated method stub
				return 0;
			}
			
			@Override
			public Iterator<Object> iterator() {
				// TODO Auto-generated method stub
				return null;
			}
			
			@Override
			public boolean isEmpty() {
				// TODO Auto-generated method stub
				return false;
			}
			
			@Override
			public int indexOf(Object o) {
				// TODO Auto-generated method stub
				return 0;
			}
			
			@Override
			public Object get(int index) {
				// TODO Auto-generated method stub
				return null;
			}
			
			@Override
			public boolean containsAll(Collection<?> c) {
				// TODO Auto-generated method stub
				return false;
			}
			
			@Override
			public boolean contains(Object o) {
				// TODO Auto-generated method stub
				return false;
			}
			
			@Override
			public void clear() {
				// TODO Auto-generated method stub
				
			}
			
			@Override
			public boolean addAll(int index, Collection<? extends Object> c) {
				// TODO Auto-generated method stub
				return false;
			}
			
			@Override
			public boolean addAll(Collection<? extends Object> c) {
				// TODO Auto-generated method stub
				return false;
			}
			
			@Override
			public void add(int index, Object element) {
				// TODO Auto-generated method stub
				
			}
			
			@Override
			public boolean add(Object e) {
				// TODO Auto-generated method stub
				return false;
			}
		};
    }
    
    public OurClass.MyClass2 bar(String a, boolean b, OurClass.MyClass2 c){
    	return null;
    }
    
    private OurClass.MyClass2 hoho;
    
    public static class MyClass2 {
        
        public void foo() {
            System.out.println(MyClass.A);
        }
        
        public static class MyClass3 {}
        
    }
    

}
