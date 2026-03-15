package com.inventory_service.inventory_service.dto;

import java.math.BigDecimal;

public class InventoryStyleDto {
    private int styleId;
    private String itemName;
    private String itemType;
    private BigDecimal rentalFee;
    private BigDecimal deposit;
    public InventoryStyleDto() {
    }
    public InventoryStyleDto(int styleId, String itemName, String itemType, BigDecimal rentalFee, BigDecimal deposit) {
        this.styleId = styleId;
        this.itemName = itemName;
        this.itemType = itemType;
        this.rentalFee = rentalFee;
        this.deposit = deposit;
    }
    public int getStyleId() {
        return styleId;
    }
    public void setStyleId(int styleId) {
        this.styleId = styleId;
    }
    public String getItemName() {
        return itemName;
    }
    public void setItemName(String itemName) {
        this.itemName = itemName;
    }
    public String getItemType() {
        return itemType;
    }
    public void setItemType(String itemType) {
        this.itemType = itemType;
    }
    public BigDecimal getRentalFee() {
        return rentalFee;
    }
    public void setRentalFee(BigDecimal rentalFee) {
        this.rentalFee = rentalFee;
    }
    public BigDecimal getDeposit() {
        return deposit;
    }
    public void setDeposit(BigDecimal deposit) {
        this.deposit = deposit;
    }

    


    
}