package ru.csu.stan.java.cfg.automaton;

import java.math.BigInteger;
import java.util.List;

/**
 * 
 * @author mz
 *
 */
class FlowCursor
{
    private int currentId = 1;
    private List<Integer> parentIds;
    
    public int getCurrentId()
    {
        return currentId;
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
}
