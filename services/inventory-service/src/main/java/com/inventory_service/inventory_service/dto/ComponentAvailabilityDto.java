package com.inventory_service.inventory_service.dto;

public class ComponentAvailabilityDto {
    private InventoryDto inventoryDto;
    private int availableQty;
    
    public ComponentAvailabilityDto() {
        
    }
    
    public ComponentAvailabilityDto(InventoryDto inventoryDto, int availableQty) {
        this.inventoryDto = inventoryDto;
        this.availableQty = availableQty;
    }

    public InventoryDto getInventoryDto() {
        return inventoryDto;
    }
    public void setInventoryDto(InventoryDto inventoryDto) {
        this.inventoryDto = inventoryDto;
    }
    public int getAvailableQty() {
        return availableQty;
    }
    public void setAvailableQty(int availableQty) {
        this.availableQty = availableQty;
    }

    
    
}
