package com.inventory_service.inventory_service.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import com.inventory_service.inventory_service.entity.InventoryQuantityTrack;
import com.inventory_service.inventory_service.entity.InventoryQuantityTrackId;


@Repository
public interface InventoryQuantityTrackRepository  extends JpaRepository<InventoryQuantityTrack,InventoryQuantityTrackId>{
    @Query(
    "SELECT u FROM InventoryQuantityTrack u WHERE (u.model.modelId = :modelId) AND (:date>=u.date)")
    List<InventoryQuantityTrack> getInventoryQuantityTrackByIdAfterDate(@Param("modelId") String modelId,@Param("date") LocalDate date );
 
    @Query(
    "SELECT u FROM InventoryQuantityTrack u WHERE u.date = (" +
    "SELECT MAX(t.date) FROM InventoryQuantityTrack t WHERE t.model.modelId = u.model.modelId AND t.date <= :date" +
    ")")
    List<InventoryQuantityTrack> getLatestInventoryQuantityTrackForDate(@Param("date") LocalDate date);

    Optional<InventoryQuantityTrack> findFirstByModel_ModelIdAndDateLessThanEqualOrderByDateDesc(String modelId, LocalDate date);

    
} 
