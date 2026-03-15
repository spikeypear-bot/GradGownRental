package com.inventory_service.inventory_service.entity;

import java.io.Serializable;





public class ItemHoldId implements Serializable{
    
    private String holdId;
    private String model;
    public ItemHoldId(String holdId, String model) {
        this.holdId = holdId;
        this.model = model;
    }
    public ItemHoldId() {
    }
    public String getHoldId() {
        return holdId;
    }
    public void setHoldId(String holdId) {
        this.holdId = holdId;
    }
    public String getModel() {
        return model;
    }
    public void setModel(String model) {
        this.model = model;
    }
    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((holdId == null) ? 0 : holdId.hashCode());
        result = prime * result + ((model == null) ? 0 : model.hashCode());
        return result;
    }
    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        ItemHoldId other = (ItemHoldId) obj;
        if (holdId == null) {
            if (other.holdId != null)
                return false;
        } else if (!holdId.equals(other.holdId))
            return false;
        if (model == null) {
            if (other.model != null)
                return false;
        } else if (!model.equals(other.model))
            return false;
        return true;
    }
    

    
    
    
    


    
}