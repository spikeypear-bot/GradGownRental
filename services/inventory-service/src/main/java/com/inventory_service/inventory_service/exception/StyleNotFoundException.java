package com.inventory_service.inventory_service.exception;

public class StyleNotFoundException extends RuntimeException{

    public StyleNotFoundException() {
        super("Error: Style cannot be found.");
    }

    public StyleNotFoundException(String message) {
        super(message);
    }

    
    
}
