package com.inventory_service.inventory_service.entity;


import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;


@Entity
@Table(name = "\"itemhold\"")
@IdClass(ItemHoldId.class)
public class ItemHold {
    @Id
    @Column(name="hold_id")
    private String holdId;
    @Id
    @ManyToOne
    @JoinColumn(name="model_id")
    private Inventory model;
    @Column(name="qty")
    private int qty;
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    public ItemHold() {
    }
    public ItemHold(String holdId, Inventory model, int qty, LocalDateTime createdAt) {
        this.holdId = holdId;
        this.model = model;
        this.qty = qty;
        this.createdAt = createdAt;
    }
    public String getHoldId() {
        return holdId;
    }
    public void setHoldId(String holdId) {
        this.holdId = holdId;
    }
    public Inventory getModel() {
        return model;
    }
    public void setModel(Inventory model) {
        this.model = model;
    }
    public int getQty() {
        return qty;
    }
    public void setQty(int qty) {
        this.qty = qty;
    }
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
   

    
    
    
    

    
}
