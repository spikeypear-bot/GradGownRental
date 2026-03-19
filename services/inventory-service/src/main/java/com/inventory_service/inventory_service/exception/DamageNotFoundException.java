package com.inventory_service.inventory_service.exception;

import java.util.List;

public class DamageNotFoundException extends RuntimeException{

    List<Integer> errors;

    
    public DamageNotFoundException() {
        super("Error: Damage records cannot be found.");
    }


    public DamageNotFoundException(String message) {
        super(message);
    }


    public DamageNotFoundException( List<Integer> errors) {
        super("Damage records with that quantity cannot be found.");
        this.errors = errors;
    }


    public List<Integer> getErrors() {
        return errors;
    }


    public void setErrors(List<Integer> errors) {
        this.errors = errors;
    }
    
    
}
