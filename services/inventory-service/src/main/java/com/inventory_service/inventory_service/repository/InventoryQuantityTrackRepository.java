package com.inventory_service.inventory_service.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

import com.inventory_service.inventory_service.entity.InventoryQuantityTrack;
import com.inventory_service.inventory_service.entity.InventoryQuantityTrackId;


@Repository
public interface InventoryQuantityTrackRepository  extends JpaRepository<InventoryQuantityTrack,InventoryQuantityTrackId>{
    @Query(
    "SELECT u FROM InventoryQuantityTrack u WHERE (u.model.modelId = :modelId) AND (:date>=u.date)")
    List<InventoryQuantityTrack> getInventoryQuantityTrackByIdAfterDate(@Param("modelId") String modelId,@Param("date") LocalDate date );
    

    
} 