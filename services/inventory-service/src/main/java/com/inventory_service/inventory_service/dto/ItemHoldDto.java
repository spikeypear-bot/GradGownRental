package com.inventory_service.inventory_service.dto;


import java.time.LocalDateTime;

import com.inventory_service.inventory_service.entity.Inventory;

public class ItemHoldDto {
    private String  holdId;
    private Inventory model;
    private int qty;
    private LocalDateTime createdAt;
    public ItemHoldDto(String holdId, Inventory model, int qty, LocalDateTime createdAt) {
        this.holdId = holdId;
        this.model = model;
        this.qty = qty;
        this.createdAt = createdAt;
    }
    
    public ItemHoldDto() {
    }

    public String getHoldId() {
        return holdId;
    }
    public void setHoldId(String holdId) {
        this.holdId = holdId;
    }
    public Inventory getModel() {
        return model;
    }
    public void setModel(Inventory model) {
        this.model = model;
    }
    public int getQty() {
        return qty;
    }
    public void setQty(int qty) {
        this.qty = qty;
    }
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    
    
    
    
    
    
    
}
