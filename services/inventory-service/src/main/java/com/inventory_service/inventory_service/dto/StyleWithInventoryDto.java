package com.inventory_service.inventory_service.dto;

import java.util.List;

public class StyleWithInventoryDto {
    private InventoryStyleDto inventoryStyle;

    private List<ModelOnlyDto> models;

    public StyleWithInventoryDto(InventoryStyleDto inventoryStyle, List<ModelOnlyDto> models) {
        this.inventoryStyle = inventoryStyle;
        this.models = models;
    }

    public StyleWithInventoryDto() {
    }

    public InventoryStyleDto getInventoryStyle() {
        return inventoryStyle;
    }

    public void setInventoryStyle(InventoryStyleDto inventoryStyle) {
        this.inventoryStyle = inventoryStyle;
    }

    public List<ModelOnlyDto> getModels() {
        return models;
    }

    public void setModels(List<ModelOnlyDto> models) {
        this.models = models;
    }

    

    
}
