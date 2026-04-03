package com.inventory_service.inventory_service.dto;

public class StockOverviewRowDto {
    private String modelId;
    private String itemName;
    private String itemType;
    private String size;
    private int totalQty;
    private int availableQty;
    private int reservedQty;
    private int rentedQty;
    private int damagedQty;
    private int repairQty;
    private int washQty;
    private int backupQty;

    public StockOverviewRowDto() {
    }

    public StockOverviewRowDto(String modelId, String itemName, String itemType, String size, int totalQty,
            int availableQty, int reservedQty, int rentedQty, int damagedQty, int repairQty, int washQty,
            int backupQty) {
        this.modelId = modelId;
        this.itemName = itemName;
        this.itemType = itemType;
        this.size = size;
        this.totalQty = totalQty;
        this.availableQty = availableQty;
        this.reservedQty = reservedQty;
        this.rentedQty = rentedQty;
        this.damagedQty = damagedQty;
        this.repairQty = repairQty;
        this.washQty = washQty;
        this.backupQty = backupQty;
    }

    public String getModelId() {
        return modelId;
    }

    public void setModelId(String modelId) {
        this.modelId = modelId;
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

    public int getDamagedQty() {
        return damagedQty;
    }

    public void setDamagedQty(int damagedQty) {
        this.damagedQty = damagedQty;
    }

    public int getRepairQty() {
        return repairQty;
    }

    public void setRepairQty(int repairQty) {
        this.repairQty = repairQty;
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
