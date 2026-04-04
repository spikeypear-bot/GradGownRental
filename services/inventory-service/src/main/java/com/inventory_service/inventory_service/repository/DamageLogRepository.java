package com.inventory_service.inventory_service.repository;

import java.time.LocalDate;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.inventory_service.inventory_service.entity.DamageLog;

@Repository
public interface DamageLogRepository extends JpaRepository<DamageLog,Integer> {
    @Query(" SELECT COALESCE(SUM(d.quantity), 0) FROM DamageLog d WHERE d.model.modelId = :modelId AND d.date <= :targetDate AND (d.dateRepaired IS NULL OR d.dateRepaired > :targetDate)")
    public int getActiveDamagedQty(@Param("modelId") String  modelId,@Param("targetDate") LocalDate targetDate);

    List<DamageLog> findByModel_ModelIdAndDateRepairedIsNullOrderByDateAsc(String modelId);

    
} 
