package com.inventory_service.inventory_service.dto;

import com.inventory_service.inventory_service.entity.InventoryStyle;

public class InventoryDto{
    
    private String modelId;
    private InventoryStyle style;
    private String size;
    private int totalQty;
    
    public InventoryDto(String modelId, InventoryStyle style, String size, int totalQty) {
        this.modelId = modelId;
        this.style = style;
        this.size = size;
        this.totalQty = totalQty;
    }
    public InventoryDto() {
    }
    public String getModelId() {
        return modelId;
    }
    public void setModelId(String modelId) {
        this.modelId = modelId;
    }
    public InventoryStyle getStyle() {
        return style;
    }
    public void setStyle(InventoryStyle style) {
        this.style = style;
    }
    public String getSize() {
        return size;
    }
    public void setSize(String size) {
        this.size = size;
    }
    public int getTotalQty() {
        return totalQty;
    }
    public void setTotalQty(int totalQty) {
        this.totalQty = totalQty;
    }
    
    

   

    

}