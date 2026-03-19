package com.inventory_service.inventory_service.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.inventory_service.inventory_service.entity.GraduationPackage;

import java.util.List;



@Repository
public interface GraduationPackageRepository extends JpaRepository<GraduationPackage,Integer> {

    @Query("SELECT p from GraduationPackage p WHERE (:institution is NULL or p.institution LIKE :institution) AND (:educationLevel is NULL or p.educationLevel LIKE :educationLevel) AND(:faculty is NULL or p.faculty LIKE :faculty)")
    List<GraduationPackage> findByEducationLevelAndInstitutionAndFaculty(
        @Param("educationLevel") String educationLevel,
        @Param("institution")  String institution,
        @Param("faculty")String faculty
    );

    
}
