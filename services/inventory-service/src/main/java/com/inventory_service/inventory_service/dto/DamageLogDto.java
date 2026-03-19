package com.inventory_service.inventory_service.dto;

import java.time.LocalDate;

import com.inventory_service.inventory_service.entity.Inventory;

public class DamageLogDto {
    
    private Integer damageId;
    private Inventory model;
    private int quantity;
    private String reason;
    private LocalDate date;
    private LocalDate dateRepaired;
    
    public DamageLogDto() {
    }

    public DamageLogDto(Integer damageId, Inventory model, int quantity, String reason, LocalDate date,
            LocalDate dateRepaired) {
        this.damageId = damageId;
        this.model = model;
        this.quantity = quantity;
        this.reason = reason;
        this.date = date;
        this.dateRepaired = dateRepaired;
    }

    public Integer getDamageId() {
        return damageId;
    }

    public void setDamageId(Integer damageId) {
        this.damageId = damageId;
    }

    public Inventory getModel() {
        return model;
    }

    public void setModel(Inventory model) {
        this.model = model;
    }

    public int getQuantity() {
        return quantity;
    }

    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public LocalDate getDate() {
        return date;
    }

    public void setDate(LocalDate date) {
        this.date = date;
    }

    public LocalDate getDateRepaired() {
        return dateRepaired;
    }

    public void setDateRepaired(LocalDate dateRepaired) {
        this.dateRepaired = dateRepaired;
    }
    
    

    

}
