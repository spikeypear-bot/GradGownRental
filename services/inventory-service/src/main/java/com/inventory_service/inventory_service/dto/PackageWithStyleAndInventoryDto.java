package com.inventory_service.inventory_service.dto;

import java.math.BigDecimal;

public class PackageWithStyleAndInventoryDto {
    private Integer packageId;
    private String educationLevel;
    private String institution;
    private String faculty;
    private StyleWithInventoryDto hatStyle;
    private StyleWithInventoryDto gownStyle;
    private StyleWithInventoryDto hoodStyle;
    private BigDecimal totalDeposit;
    private BigDecimal totalRentalFee;
    private BigDecimal totalPrice;
    public PackageWithStyleAndInventoryDto(Integer packageId, String educationLevel, String institution, String faculty,
            StyleWithInventoryDto hatStyle, StyleWithInventoryDto gownStyle, StyleWithInventoryDto hoodStyle,
            BigDecimal totalDeposit, BigDecimal totalRentalFee, BigDecimal totalPrice) {
        this.packageId = packageId;
        this.educationLevel = educationLevel;
        this.institution = institution;
        this.faculty = faculty;
        this.hatStyle = hatStyle;
        this.gownStyle = gownStyle;
        this.hoodStyle = hoodStyle;
        this.totalDeposit = totalDeposit;
        this.totalRentalFee = totalRentalFee;
        this.totalPrice = totalPrice;
    }
    public PackageWithStyleAndInventoryDto() {
    }
    public Integer getPackageId() {
        return packageId;
    }
    public void setPackageId(Integer packageId) {
        this.packageId = packageId;
    }
    public String getEducationLevel() {
        return educationLevel;
    }
    public void setEducationLevel(String educationLevel) {
        this.educationLevel = educationLevel;
    }
    public String getInstitution() {
        return institution;
    }
    public void setInstitution(String institution) {
        this.institution = institution;
    }
    public String getFaculty() {
        return faculty;
    }
    public void setFaculty(String faculty) {
        this.faculty = faculty;
    }
    public StyleWithInventoryDto getHatStyle() {
        return hatStyle;
    }
    public void setHatStyle(StyleWithInventoryDto hatStyle) {
        this.hatStyle = hatStyle;
    }
    public StyleWithInventoryDto getGownStyle() {
        return gownStyle;
    }
    public void setGownStyle(StyleWithInventoryDto gownStyle) {
        this.gownStyle = gownStyle;
    }
    public StyleWithInventoryDto getHoodStyle() {
        return hoodStyle;
    }
    public void setHoodStyle(StyleWithInventoryDto hoodStyle) {
        this.hoodStyle = hoodStyle;
    }
    public BigDecimal getTotalDeposit() {
        return totalDeposit;
    }
    public void setTotalDeposit(BigDecimal totalDeposit) {
        this.totalDeposit = totalDeposit;
    }
    public BigDecimal getTotalRentalFee() {
        return totalRentalFee;
    }
    public void setTotalRentalFee(BigDecimal totalRentalFee) {
        this.totalRentalFee = totalRentalFee;
    }
    public BigDecimal getTotalPrice() {
        return totalPrice;
    }
    public void setTotalPrice(BigDecimal totalPrice) {
        this.totalPrice = totalPrice;
    }



    
}
