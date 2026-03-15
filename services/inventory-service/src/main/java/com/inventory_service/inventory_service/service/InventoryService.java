package com.inventory_service.inventory_service.service;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.inventory_service.inventory_service.dto.InventoryDto;
import com.inventory_service.inventory_service.entity.Inventory;
import com.inventory_service.inventory_service.mapper.InventoryMapper;
import com.inventory_service.inventory_service.repository.InventoryRepository;


@Service
public class InventoryService {
    private final InventoryRepository inventoryRepository;
    private final InventoryMapper inventoryMapper;

    public InventoryService(InventoryRepository inventoryRepository, InventoryMapper inventoryMapper) {
        this.inventoryRepository = inventoryRepository; 
        this.inventoryMapper=inventoryMapper;// final field initialized here
    }


    public List<InventoryDto> getInventoryByStyleId(int styleId){
        List<Inventory> inventories=inventoryRepository.findAllByStyle_StyleId(styleId);
        if(inventories==null || inventories.isEmpty()){
            return Collections.emptyList();
        }
        else{
            return inventoryMapper.inventoriesToInventoryDtos(inventories);
        }
        
        
       
    }
    public List<InventoryDto> getAllInventory(){
        return inventoryMapper.inventoriesToInventoryDtos((inventoryRepository.findAll()));
    }
    public InventoryDto getByModelId(String modelId) throws RuntimeException{
        Optional<Inventory> res=inventoryRepository.findById(modelId);
        
        if(res.isPresent()){
            return inventoryMapper.inventoryToInventoryDto(res.get());
        }
        else{
            throw new RuntimeException("No models found.");

    }}

    
    



    
}
