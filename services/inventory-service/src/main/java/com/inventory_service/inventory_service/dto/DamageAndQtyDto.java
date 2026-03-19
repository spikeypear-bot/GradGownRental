package com.inventory_service.inventory_service.dto;

public class DamageAndQtyDto {
    private Integer damageId;
    private int quantity;
    public DamageAndQtyDto(Integer damageId, int quantity) {
        this.damageId = damageId;
        this.quantity = quantity;
    }
    public Integer getDamageId() {
        return damageId;
    }
    public void setDamageId(Integer damageId) {
        this.damageId = damageId;
    }
    public int getQuantity() {
        return quantity;
    }
    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }
    public DamageAndQtyDto() {
    }
    
    
}
