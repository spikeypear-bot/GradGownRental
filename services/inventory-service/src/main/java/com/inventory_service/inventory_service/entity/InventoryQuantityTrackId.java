package com.inventory_service.inventory_service.entity;

import java.io.Serializable;
import java.time.LocalDate;


public class InventoryQuantityTrackId implements Serializable{
    private String model;
    private LocalDate date;
    public InventoryQuantityTrackId() {
    }

    public InventoryQuantityTrackId(String model, LocalDate date) {
        this.model = model;
        this.date = date;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((model == null) ? 0 : model.hashCode());
        result = prime * result + ((date == null) ? 0 : date.hashCode());
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
        InventoryQuantityTrackId other = (InventoryQuantityTrackId) obj;
        if (model == null) {
            if (other.model != null)
                return false;
        } else if (!model.equals(other.model))
            return false;
        if (date == null) {
            if (other.date != null)
                return false;
        } else if (!date.equals(other.date))
            return false;
        return true;
    }
    

    

    


    
}
