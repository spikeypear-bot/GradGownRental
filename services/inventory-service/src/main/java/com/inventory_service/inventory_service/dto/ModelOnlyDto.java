package com.inventory_service.inventory_service.dto;


public class ModelOnlyDto {
    private String modelId;
    private String size;
    private int totalQty;
    public ModelOnlyDto(String modelId, String size, int totalQty) {
        this.modelId = modelId;
        this.size = size;
        this.totalQty = totalQty;
    }
    public ModelOnlyDto() {
    }
    public String getModelId() {
        return modelId;
    }
    public void setModelId(String modelId) {
        this.modelId = modelId;
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
