package com.inventory_service.inventory_service.entity;

import java.math.BigDecimal;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

//Refers to the different styles, example like Blue Gown, or Crimson Edge Hood, these two would be different style. All styles have same rental fee and deposit. 


@Entity
@Table(name="\"inventorystyle\"")
public class InventoryStyle {
    @Id
    @Column(name="style_id")
    private int styleId;
    @Column(name="item_name")
    private String itemName;
    @Column(name="item_type")
    private String itemType;
    @Column(name="rental_fee")
    private BigDecimal rentalFee;
    @Column(name="deposit")
    private BigDecimal deposit;
    public InventoryStyle() {
    }
    public InventoryStyle(int styleId, String itemName, String itemType, BigDecimal rentalFee, BigDecimal deposit) {
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
