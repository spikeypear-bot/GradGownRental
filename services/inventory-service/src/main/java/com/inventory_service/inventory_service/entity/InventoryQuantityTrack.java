package com.inventory_service.inventory_service.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.time.LocalDate;

// Tracks inventory movement day by day for each model.
// This now mirrors the operational scenario states:
// available -> reserved -> rented -> damaged/repair -> wash -> available.
// Backup is retained as the overflow buffer used by the current service logic.
//When a gown is reserved it would be blocked for 7 days, 3 days being rented and 4 days being sent for washing. 



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
    @Column(name = "available_qty")
    private int availableQty;
    @Column(name = "reserved_qty")
    private int reservedQty;
    @Column(name = "rented_qty")
    private int rentedQty;
    @Column(name="wash_qty")
    private int washQty;
    @Column(name="backup_qty")
    private int backupQty;
    
    public InventoryQuantityTrack() {
    }
    

    public InventoryQuantityTrack(LocalDate date, Inventory model, int reservedQty, int rentedQty, int washQty,
            int backupQty) {
        this(date, model, 0, reservedQty, rentedQty, washQty, backupQty);
    }

    public InventoryQuantityTrack(LocalDate date, Inventory model, int availableQty, int reservedQty, int rentedQty,
            int washQty, int backupQty) {
        this.date = date;
        this.model = model;
        this.availableQty = availableQty;
        this.reservedQty = reservedQty;
        this.rentedQty = rentedQty;
        this.washQty = washQty;
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

    public int getAvailableQty() {
        return availableQty;
    }

    public void setAvailableQty(int availableQty) {
        this.availableQty = availableQty;
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

    public int getBackupQty() {
        return backupQty;
    }

    public void setBackupQty(int backupQty) {
        this.backupQty = backupQty;
    }

    
    
    

    




    
    
}
