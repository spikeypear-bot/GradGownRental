package com.inventory_service.inventory_service.dto;

import java.time.LocalDate;
import java.util.List;

public class DailyAvailabilityDto {
    private LocalDate date;
    private List<ComponentAvailabilityDto> components;
    private int totalAvailable;
    public DailyAvailabilityDto(LocalDate date, List<ComponentAvailabilityDto> components, int totalAvailable) {
        this.date = date;
        this.components = components;
        this.totalAvailable = totalAvailable;
    }
    public LocalDate getDate() {
        return date;
    }
    public void setDate(LocalDate date) {
        this.date = date;
    }
    public List<ComponentAvailabilityDto> getComponents() {
        return components;
    }
    public void setComponents(List<ComponentAvailabilityDto> components) {
        this.components = components;
    }
    public int getTotalAvailable() {
        return totalAvailable;
    }
    public void setTotalAvailable(int totalAvailable) {
        this.totalAvailable = totalAvailable;
    }
    public DailyAvailabilityDto() {
    }

    
}
