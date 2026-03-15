package com.inventory_service.inventory_service.dto;

import java.time.LocalDate;

public class InventoryDateAndQuantityDto {
    private InventoryDto inventoryDto;
    private LocalDate date;
    private int availableQty;
    public InventoryDateAndQuantityDto(InventoryDto inventoryDto, LocalDate date, int availableQty) {
        this.inventoryDto = inventoryDto;
        this.date = date;
        this.availableQty = availableQty;
    }
    public InventoryDateAndQuantityDto() {
    }
    public InventoryDto getInventoryDto() {
        return inventoryDto;
    }
    public void setInventoryDto(InventoryDto inventoryDto) {
        this.inventoryDto = inventoryDto;
    }
    public LocalDate getDate() {
        return date;
    }
    public void setDate(LocalDate date) {
        this.date = date;
    }
    public int getAvailableQty() {
        return availableQty;
    }
    public void setAvailableQty(int availableQty) {
        this.availableQty = availableQty;
    }
    

    
    
}
