package ru.csu.stan.java.cfg.util.scope;

/**
 * 
 * @author mz
 *
 */
public class VariableFromScope {
	private String name;
	private String type;
	private String modifier;
	
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
	
	public String getModifier() {
		return modifier;
	}
	
	public void setModifier(String modifier) {
		this.modifier = modifier;
	}

	@Override
	public boolean equals(Object arg0) {
		if (arg0 instanceof VariableFromScope){
			if (name.equals(((VariableFromScope) arg0).name) &&
					type.equals(((VariableFromScope) arg0).type) &&
					modifier.equals(((VariableFromScope) arg0).modifier))
				return true;
			else
				return false;
		}
		else
			return false;
	}

	@Override
	public int hashCode() {
		return String.valueOf(name).hashCode()*31*31 + String.valueOf(type).hashCode()*31 + String.valueOf(modifier).hashCode();
	}
	
	
}
