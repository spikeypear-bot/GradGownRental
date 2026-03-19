package com.inventory_service.inventory_service.mapper;

import java.util.List;

import org.mapstruct.Mapper;

import com.inventory_service.inventory_service.dto.InventoryDto;
import com.inventory_service.inventory_service.entity.Inventory;



@Mapper(componentModel = "spring",uses={InventoryStyleMapper.class})



public interface InventoryMapper {
    InventoryDto inventoryToInventoryDto(Inventory inventory);
    Inventory inventoryDtoToInventory(InventoryDto inventoryDto);
    List<InventoryDto> inventoriesToInventoryDtos(List<Inventory> inventories);
    List<Inventory> inventoryDtosToInventories(List<InventoryDto> dtos);
    

    
} 