package com.inventory_service.inventory_service.dto;

import java.time.LocalDate;

import com.inventory_service.inventory_service.entity.Inventory;

public class InventoryQuantityTrackDto {
    
    private LocalDate date;
    private Inventory model;
    private int reservedQty;
    private int rentedQty;
    private int washQty;
    
    private int backupQty;

    public InventoryQuantityTrackDto(LocalDate date, Inventory model, int reservedQty, int rentedQty, int washQty,
            int backupQty) {
        this.date = date;
        this.model = model;
        this.reservedQty = reservedQty;
        this.rentedQty = rentedQty;
        this.washQty = washQty;
        this.backupQty = backupQty;
    }

    public InventoryQuantityTrackDto() {
    }

    public LocalDate getDate() {
        return date;
    }

    public void setDate(LocalDate date) {
        this.date = date;
    }

    public Inventory getModel() {
        return model;
    }

    public void setModel(Inventory model) {
        this.model = model;
    }

    public int getReservedQty() {
        return reservedQty;
    }

    public void setReservedQty(int reservedQty) {
        this.reservedQty = reservedQty;
    }

    public int getRentedQty() {
        return rentedQty;
    }

    public void setRentedQty(int rentedQty) {
        this.rentedQty = rentedQty;
    }

    public int getWashQty() {
        return washQty;
    }

    public void setWashQty(int washQty) {
        this.washQty = washQty;
    }

    public int getBackupQty() {
        return backupQty;
    }

    public void setBackupQty(int backupQty) {
        this.backupQty = backupQty;
    }
    
    
    
    
    

    
}
