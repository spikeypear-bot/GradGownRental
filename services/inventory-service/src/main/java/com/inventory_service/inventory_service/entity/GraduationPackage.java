package com.inventory_service.inventory_service.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

@Entity
@Table(name="\"package\"")
public class GraduationPackage {
    
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name="package_id")
    private Integer packageId;
    @Column(name="education_level")
    private String educationLevel;
    @Column(name="institution")
    private String institution;
    @Column(name="faculty")
    private String faculty;

    @ManyToOne
    @JoinColumn(name="hat_style_id")
    private InventoryStyle hatStyle;
    @ManyToOne
    @JoinColumn(name="hood_style_id")
    private InventoryStyle hoodStyle;
    @ManyToOne
    @JoinColumn(name="gown_style_id")
    private InventoryStyle gownStyle;
    public GraduationPackage() {
    }
    public GraduationPackage(Integer packageId, String educationLevel, String institution, String faculty,
            InventoryStyle hatStyle, InventoryStyle hoodStyle, InventoryStyle gownStyle) {
        this.packageId = packageId;
        this.educationLevel = educationLevel;
        this.institution = institution;
        this.faculty = faculty;
        this.hatStyle = hatStyle;
        this.hoodStyle = hoodStyle;
        this.gownStyle = gownStyle;
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
    public InventoryStyle getHatStyle() {
        return hatStyle;
    }
    public void setHatStyle(InventoryStyle hatStyle) {
        this.hatStyle = hatStyle;
    }
    public InventoryStyle getHoodStyle() {
        return hoodStyle;
    }
    public void setHoodStyle(InventoryStyle hoodStyle) {
        this.hoodStyle = hoodStyle;
    }
    public InventoryStyle getGownStyle() {
        return gownStyle;
    }
    public void setGownStyle(InventoryStyle gownStyle) {
        this.gownStyle = gownStyle;
    }
    
    
    
    
}
