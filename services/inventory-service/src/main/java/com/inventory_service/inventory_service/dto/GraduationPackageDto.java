package com.inventory_service.inventory_service.dto;

public class GraduationPackageDto{
    private Integer packageId;
    private String educationLevel;
    private String institution;
    private String faculty;
    private InventoryStyleDto hatStyle;
    private InventoryStyleDto hoodStyle;
    private InventoryStyleDto gownStyle;
    public GraduationPackageDto(Integer packageId, String educationLevel, String institution, String faculty,
            InventoryStyleDto hatStyle, InventoryStyleDto hoodStyle, InventoryStyleDto gownStyle) {
        this.packageId = packageId;
        this.educationLevel = educationLevel;
        this.institution = institution;
        this.faculty = faculty;
        this.hatStyle = hatStyle;
        this.hoodStyle = hoodStyle;
        this.gownStyle = gownStyle;
    }
    public GraduationPackageDto() {
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
    public InventoryStyleDto getHatStyle() {
        return hatStyle;
    }
    public void setHatStyle(InventoryStyleDto hatStyle) {
        this.hatStyle = hatStyle;
    }
    public InventoryStyleDto getHoodStyle() {
        return hoodStyle;
    }
    public void setHoodStyle(InventoryStyleDto hoodStyle) {
        this.hoodStyle = hoodStyle;
    }
    public InventoryStyleDto getGownStyle() {
        return gownStyle;
    }
    public void setGownStyle(InventoryStyleDto gownStyle) {
        this.gownStyle = gownStyle;
    }

    
   
    
    
   
    
    

    

}