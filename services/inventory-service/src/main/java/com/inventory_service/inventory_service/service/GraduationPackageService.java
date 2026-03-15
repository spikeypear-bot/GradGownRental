package com.inventory_service.inventory_service.service;

import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.inventory_service.inventory_service.dto.GraduationPackageDto;
import com.inventory_service.inventory_service.entity.GraduationPackage;
import com.inventory_service.inventory_service.mapper.GraduationPackageMapper;
import com.inventory_service.inventory_service.repository.GraduationPackageRepository;



@Service
public class GraduationPackageService {
    private final GraduationPackageMapper graduationPackageMapper;
    private final GraduationPackageRepository graduationPackageRepository;
    
    public GraduationPackageService(GraduationPackageMapper graduationPackageMapper,
            GraduationPackageRepository graduationPackageRepository) {
        this.graduationPackageMapper = graduationPackageMapper;
        this.graduationPackageRepository = graduationPackageRepository;
        
    }
    
    public List<GraduationPackageDto> getGraduationPackageByEducationLevelAndInstitutionAndFaculty(String educationLevel,String institution,String faculty){
        List<GraduationPackage> graduationPackages=this.graduationPackageRepository.findByEducationLevelAndInstitutionAndFaculty(educationLevel, institution, faculty);
        List<GraduationPackageDto> res= this.graduationPackageMapper.graduationPackagesToGraduationPackageDtos(graduationPackages);
        return res;

    }
    public List<GraduationPackageDto> getAllGraduationPackages(){
        List <GraduationPackage> graduationPackages= this.graduationPackageRepository.findAll();
        List<GraduationPackageDto> res= this.graduationPackageMapper.graduationPackagesToGraduationPackageDtos(graduationPackages);
        return res;
        
    }
    public GraduationPackageDto getByPackageId (int packageId) throws RuntimeException{
        Optional<GraduationPackage> res=this.graduationPackageRepository.findById(packageId);
        
        if(res.isPresent()){
            return graduationPackageMapper.graduationPackageToGraduationPackageDto(res.get());
        }
        else{
            throw new RuntimeException("Package not found");

    }}

    
    

    

    
}
