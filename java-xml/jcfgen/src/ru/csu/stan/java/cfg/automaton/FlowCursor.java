package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;
import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;

/**
 * 
 * @author mz
 *
 */
class FlowCursor implements Cloneable
{
    private int currentId = 1;
    private Set<Integer> parentIds = new LinkedHashSet<Integer>();
    
    public int getCurrentId()
    {
        return currentId;
    }
    
    public void setCurrentId(int value){
        this.currentId = value;
    }
    
    public BigInteger getCurrentIdBigInteger(){
    	return BigInteger.valueOf(currentId);
    }
        
    public void incrementCurrentId()
    {
        this.currentId++;
    }
    
    public List<Integer> getParentIds()
    {
        return new LinkedList<Integer>(parentIds);
    }
    
    public void clearParentIds(){
    	for (Iterator<Integer> it = parentIds.iterator(); it.hasNext();){
    		if (it.next().intValue() > 0)
    			it.remove();
    	}
    }
    
    public void setParentIds(List<Integer> parentIds){
    	clearParentIds();
    	for (Integer i: parentIds)
    		addParentId(i.intValue());
    }
    
    public void addParentId(int id)
    {
        this.parentIds.add(Integer.valueOf(id));
    }

    @Override
    protected FlowCursor clone()
    {
        FlowCursor newObject = new FlowCursor();
        newObject.currentId = this.currentId;
        for (Integer i: parentIds)
            newObject.addParentId(i.intValue());
        return newObject;
    }
}
