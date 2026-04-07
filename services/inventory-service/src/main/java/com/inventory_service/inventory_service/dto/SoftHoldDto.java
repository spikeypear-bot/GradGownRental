package com.inventory_service.inventory_service.dto;

import java.time.LocalDateTime;
import java.util.List;

public class SoftHoldDto {
    String holdId;
    List<ModelIdAndQtyAndDateDto> items;
    LocalDateTime createdAt;
    LocalDateTime expiresAt;
    Long createdAtEpochMs;
    Long expiresAtEpochMs;
    
    public SoftHoldDto(
        String holdId,
        List<ModelIdAndQtyAndDateDto> items,
        LocalDateTime createdAt,
        LocalDateTime expiresAt,
        Long createdAtEpochMs,
        Long expiresAtEpochMs
    ) {
        this.holdId = holdId;
        this.items = items;
        this.createdAt = createdAt;
        this.expiresAt = expiresAt;
        this.createdAtEpochMs = createdAtEpochMs;
        this.expiresAtEpochMs = expiresAtEpochMs;
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
    public LocalDateTime getExpiresAt() {
        return expiresAt;
    }
    public void setExpiresAt(LocalDateTime expiresAt) {
        this.expiresAt = expiresAt;
    }
    public Long getCreatedAtEpochMs() {
        return createdAtEpochMs;
    }
    public void setCreatedAtEpochMs(Long createdAtEpochMs) {
        this.createdAtEpochMs = createdAtEpochMs;
    }
    public Long getExpiresAtEpochMs() {
        return expiresAtEpochMs;
    }
    public void setExpiresAtEpochMs(Long expiresAtEpochMs) {
        this.expiresAtEpochMs = expiresAtEpochMs;
    }
    

}
