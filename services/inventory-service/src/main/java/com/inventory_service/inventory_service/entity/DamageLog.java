package com.inventory_service.inventory_service.entity;

import java.time.LocalDate;



import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

@Entity
@Table (name="\"damagelog\"")
public class DamageLog {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column (name="damage_id")
    private Integer damageId ;
    
    @ManyToOne 
    @JoinColumn(name ="model_id")
    private Inventory model;
    
    @Column(name ="quantity")
    private int quantity;

    @Column(name = "order_id")
    private String orderId;

    @Column (name = "reason")
    private String reason;

    @Column (name="date")
    private LocalDate date;

    @Column (name="date_repaired")
    private LocalDate dateRepaired;

    public DamageLog() {
    }

    public DamageLog(Integer damageId, Inventory model, int quantity, String orderId, String reason, LocalDate date,
            LocalDate dateRepaired) {
        this.damageId = damageId;
        this.model = model;
        this.quantity = quantity;
        this.orderId = orderId;
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

    public String getOrderId() {
        return orderId;
    }

    public void setOrderId(String orderId) {
        this.orderId = orderId;
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
