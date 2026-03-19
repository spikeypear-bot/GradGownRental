package com.inventory_service.inventory_service.dto;

import java.time.LocalDateTime;
import java.util.List;

public class SoftHoldDto {
    String holdId;
    List<ModelIdAndQtyAndDateDto> items;
    LocalDateTime createdAt;
    
    public SoftHoldDto(String holdId, List<ModelIdAndQtyAndDateDto> items, LocalDateTime createdAt) {
        this.holdId = holdId;
        this.items = items;
        this.createdAt = createdAt;
    }
    public SoftHoldDto() {
    }
    public String getHoldId() {
        return holdId;
    }
    public void setHoldId(String holdId) {
        this.holdId = holdId;
    }
    public List<ModelIdAndQtyAndDateDto> getItems() {
        return items;
    }
    public void setItems(List<ModelIdAndQtyAndDateDto> items) {
        this.items = items;
    }
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    

}
