package com.inventory_service.inventory_service.dto;

import java.math.BigDecimal;

public class PackageWithPriceDto {

    private GraduationPackageDto graduationPackageDto;
    private BigDecimal totalDeposit;
    private BigDecimal totalRentalFee;
    private BigDecimal totalPrice;
    public PackageWithPriceDto(GraduationPackageDto graduationPackageDto, BigDecimal totalDeposit, BigDecimal totalRentalFee,
            BigDecimal totalPrice) {
        this.graduationPackageDto = graduationPackageDto;
        this.totalDeposit = totalDeposit;
        this.totalRentalFee = totalRentalFee;
        this.totalPrice = totalPrice;
    }
    public PackageWithPriceDto() {
    }
    public GraduationPackageDto getGraduationPackageDto() {
        return graduationPackageDto;
    }
    public void setGraduationPackageDto(GraduationPackageDto graduationPackageDto) {
        this.graduationPackageDto = graduationPackageDto;
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
