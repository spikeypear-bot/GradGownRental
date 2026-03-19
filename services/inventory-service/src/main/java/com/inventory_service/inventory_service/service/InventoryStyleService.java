package com.inventory_service.inventory_service.service;

import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;


import com.inventory_service.inventory_service.dto.InventoryStyleDto;
import com.inventory_service.inventory_service.entity.InventoryStyle;
import com.inventory_service.inventory_service.exception.StyleNotFoundException;
import com.inventory_service.inventory_service.mapper.InventoryStyleMapper;
import com.inventory_service.inventory_service.repository.InventoryStyleRepository;


@Service
public class InventoryStyleService {
    private final InventoryStyleRepository inventoryStyleRepository;
    private final InventoryStyleMapper inventoryStyleMapper;
    public InventoryStyleService(InventoryStyleRepository inventoryStyleRepository,
            InventoryStyleMapper inventoryStyleMapper) {
        this.inventoryStyleRepository = inventoryStyleRepository;
        this.inventoryStyleMapper = inventoryStyleMapper;
    }
    
    public List<InventoryStyleDto> getAllInventoryStyle(){
        return inventoryStyleMapper.inventoryStylesToInventoryStyleDtos(inventoryStyleRepository.findAll());


    }
    public InventoryStyleDto getInventoryStyleByStyleId(int styleId) throws StyleNotFoundException{
        Optional<InventoryStyle> res= this.inventoryStyleRepository.findById(styleId);

        if(res.isPresent()){
            return inventoryStyleMapper.inventoryStyleToInventoryStyleDto(res.get());

        
        }
        else{
            throw new StyleNotFoundException();
            
        }

        
        
       
    }

    

    

}
