package com.inventory_service.inventory_service.mapper;

import java.util.List;

import org.mapstruct.Mapper;

import com.inventory_service.inventory_service.dto.GraduationPackageDto;
import com.inventory_service.inventory_service.entity.GraduationPackage;

@Mapper(componentModel = "spring", uses = {InventoryStyleMapper.class})
public interface GraduationPackageMapper{
    
    GraduationPackageDto graduationPackageToGraduationPackageDto(GraduationPackage GraduationPackage);
    GraduationPackage graduationPackageDtoToGraduationPackage(GraduationPackageDto GraduationPackageDto);
    List<GraduationPackageDto> graduationPackagesToGraduationPackageDtos(List<GraduationPackage> graduationPackages);
    List<GraduationPackage> graduationPackageDtosToGraduationPackages(List<GraduationPackageDto>graduationPackageDtos);

    
}