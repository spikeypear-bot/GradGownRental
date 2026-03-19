package com.inventory_service.inventory_service.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

//Entity keeping track of the total quantities per model, as well as the size of it. 
//Two sets of clothings are considered different model, if they have different styles (Mapped by style id), and different sizes
//Example: M Blue Gown and S Blue gown is different model, but two of the S blue gown are considered the same model id.
//Qty is mainly used for tracking.



@Entity
@Table(name="\"inventory\"")
public class Inventory {
    @Id
    @Column(name="model_id")
    private String modelId;
    @ManyToOne
    @JoinColumn(name="style_id")
    private InventoryStyle style;
    @Column(name="size")
    private String size;
    @Column(name="total_qty")
    private int totalQty;
    public Inventory() {
    }
    public Inventory(String modelId, InventoryStyle style, String size, int totalQty) {
        this.modelId = modelId;
        this.style = style;
        this.size = size;
        this.totalQty = totalQty;
    }
    public String getModelId() {
        return modelId;
    }
    public void setModelId(String modelId) {
        this.modelId = modelId;
    }
    public InventoryStyle getStyle() {
        return style;
    }
    public void setStyle(InventoryStyle style) {
        this.style = style;
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