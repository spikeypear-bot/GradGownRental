package com.inventory_service.inventory_service.repository;

import org.springframework.stereotype.Repository;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

import com.inventory_service.inventory_service.entity.Inventory;

@Repository
public interface InventoryRepository extends JpaRepository<Inventory,String>{
    //findByID(),findAllById(),findAll(),existsById(),deleteByID()
    List<Inventory> findAllByStyle_StyleId( int styleId);
    


    




}
