package com.inventory_service.inventory_service.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.inventory_service.inventory_service.entity.InventoryStyle;



@Repository
public interface InventoryStyleRepository extends JpaRepository<InventoryStyle,Integer>{
    


    
}