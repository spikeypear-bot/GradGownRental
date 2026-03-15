package com.inventory_service.inventory_service.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.time.LocalDate;
@Entity
@Table(name="\"inventoryquantitytrack\"")
@IdClass(InventoryQuantityTrackId.class)
public class InventoryQuantityTrack {
    @Id
    private LocalDate date;
    @Id
    @ManyToOne
    @JoinColumn(name="model_id")
    private Inventory model;
    @Column(name = "reserved_qty")
    private int reservedQty;
    @Column(name = "rented_qty")
    private int rentedQty;
    @Column(name="wash_qty")
    private int washQty;
    @Column(name="damaged_qty")
    private int damagedQty;
    @Column(name="backup_qty")
    private int backupQty;
    
    public InventoryQuantityTrack() {
    }
    public InventoryQuantityTrack(LocalDate date, Inventory model, int reservedQty, int rentedQty, int washQty,
            int damagedQty, int backupQty) {
        this.date = date;
        this.model = model;
        this.reservedQty = reservedQty;
        this.rentedQty = rentedQty;
        this.washQty = washQty;
        this.damagedQty = damagedQty;
        this.backupQty = backupQty;
    }
    public LocalDate getDate() {
        return date;
    }
    public void setDate(LocalDate date) {
        this.date = date;
    }
    public Inventory getModel() {
        return model;
    }
    public void setModel(Inventory model) {
        this.model = model;
    }
    public int getReservedQty() {
        return reservedQty;
    }
    public void setReservedQty(int reservedQty) {
        this.reservedQty = reservedQty;
    }
    public int getRentedQty() {
        return rentedQty;
    }
    public void setRentedQty(int rentedQty) {
        this.rentedQty = rentedQty;
    }
    public int getWashQty() {
        return washQty;
    }
    public void setWashQty(int washQty) {
        this.washQty = washQty;
    }
    public int getDamagedQty() {
        return damagedQty;
    }
    public void setDamagedQty(int damagedQty) {
        this.damagedQty = damagedQty;
    }
    public int getBackupQty() {
        return backupQty;
    }
    public void setBackupQty(int backupQty) {
        this.backupQty = backupQty;
    }
    
    
    

    




    
    
}
