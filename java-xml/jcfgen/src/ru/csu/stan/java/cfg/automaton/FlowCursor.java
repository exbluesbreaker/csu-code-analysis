package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;
import java.util.List;

/**
 * 
 * @author mz
 *
 */
class FlowCursor implements Cloneable
{
    private int currentId = 1;
    private List<Integer> parentIds;
    
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
        return parentIds;
    }
    
    public void setParentIds(List<Integer> parentIds)
    {
        this.parentIds = parentIds;
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
