package com.inventory_service.inventory_service.repository;



import java.util.List;
import java.time.LocalDateTime;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.inventory_service.inventory_service.entity.ItemHold;
import com.inventory_service.inventory_service.entity.ItemHoldId;

@Repository
public interface ItemHoldRepository extends JpaRepository<ItemHold,ItemHoldId> {
    List<ItemHold> findAllByModel_ModelId(String modelId);

    void deleteAllByHoldId(String HoldId);

    void deleteAllByCreatedAtBefore(LocalDateTime cutoff);
    
}
