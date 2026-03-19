package com.inventory_service.inventory_service.exception;

public class PackageNotFoundException extends RuntimeException {
   
    public PackageNotFoundException() {
            super("Error: Package cannot be found.");
            
        }
    

    public PackageNotFoundException(String message) {
        super(message);
        
    }

    
    
}
