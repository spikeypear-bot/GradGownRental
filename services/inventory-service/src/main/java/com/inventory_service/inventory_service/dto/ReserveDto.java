package com.inventory_service.inventory_service.dto;

import java.util.List;

public class ReserveDto {
    private String holdId;
    private List<ModelIdAndQtyAndDateDto> items;
    public ReserveDto(String holdId, List<ModelIdAndQtyAndDateDto> items) {
        this.holdId = holdId;
        this.items = items;
    }
    public ReserveDto() {
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
    
}
