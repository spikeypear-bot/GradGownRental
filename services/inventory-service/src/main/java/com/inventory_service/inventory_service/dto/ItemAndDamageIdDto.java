package com.inventory_service.inventory_service.dto;

public class ItemAndDamageIdDto {
    Integer damageId;
    ModelIdAndQtyAndDateDto modelIdAndQtyAndDateDto;
    public ItemAndDamageIdDto(Integer damageId, ModelIdAndQtyAndDateDto modelIdAndQtyAndDateDto) {
        this.damageId = damageId;
        this.modelIdAndQtyAndDateDto = modelIdAndQtyAndDateDto;
    }
    public ItemAndDamageIdDto() {
    }
    public Integer getDamageId() {
        return damageId;
    }
    public void setDamageId(Integer damageId) {
        this.damageId = damageId;
    }
    public ModelIdAndQtyAndDateDto getModelIdAndQtyAndDateDto() {
        return modelIdAndQtyAndDateDto;
    }
    public void setModelIdAndQtyAndDateDto(ModelIdAndQtyAndDateDto modelIdAndQtyAndDateDto) {
        this.modelIdAndQtyAndDateDto = modelIdAndQtyAndDateDto;
    }

}
