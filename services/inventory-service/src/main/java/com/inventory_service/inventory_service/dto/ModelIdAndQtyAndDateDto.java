package com.inventory_service.inventory_service.dto;

import java.time.LocalDate;

public class ModelIdAndQtyAndDateDto {
    private String modelId;
    private int qty;
    private LocalDate chosenDate;


    
    public ModelIdAndQtyAndDateDto(String modelId, int qty, LocalDate chosenDate) {
        this.modelId = modelId;
        this.qty = qty;
        this.chosenDate = chosenDate;
    }
    
    public ModelIdAndQtyAndDateDto() {
    }

    public String getModelId() {
        return modelId;
    }
    public void setModelId(String modelId) {
        this.modelId = modelId;
    }
    public int getQty() {
        return qty;
    }
    public void setQty(int qty) {
        this.qty = qty;
    }
    public LocalDate getChosenDate() {
        return chosenDate;
    }
    public void setChosenDate(LocalDate chosenDate) {
        this.chosenDate = chosenDate;
    }
    
    

    
    
}
