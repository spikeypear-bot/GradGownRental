package com.inventory_service.inventory_service.exception;

public class ModelNotFoundException extends RuntimeException {

    public ModelNotFoundException() {
        super("Error: Model cannot be found.");
    }

    public ModelNotFoundException(String message) {
        super(message);
    }
    
    
    
}
