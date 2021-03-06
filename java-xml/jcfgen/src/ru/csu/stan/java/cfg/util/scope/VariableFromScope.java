package ru.csu.stan.java.cfg.util.scope;

/**
 * 
 * @author mz
 *
 */
public class VariableFromScope {
	private String name;
	private String type;
	
	public String getName() {
		return name;
	}
	
	public void setName(String name) {
		this.name = name;
	}
	
	public String getType() {
		return type;
	}
	
	public void setType(String type) {
		this.type = type;
	}
	
	@Override
	public boolean equals(Object arg0) {
		if (arg0 instanceof VariableFromScope){
			if (name.equals(((VariableFromScope) arg0).name) &&
					type.equals(((VariableFromScope) arg0).type))
				return true;
			else
				return false;
		}
		else
			return false;
	}

	@Override
	public int hashCode() {
		return String.valueOf(name).hashCode()*31*31 + String.valueOf(type).hashCode()*31;
	}
	
	
}
