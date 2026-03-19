package com.inventory_service.inventory_service.mapper;

import java.util.List;

import org.mapstruct.Mapper;

import com.inventory_service.inventory_service.dto.InventoryStyleDto;
import com.inventory_service.inventory_service.entity.InventoryStyle;

@Mapper(componentModel = "spring")
public interface InventoryStyleMapper{
    InventoryStyleDto inventoryStyleToInventoryStyleDto (InventoryStyle inventoryStyle);
    InventoryStyle inventoryStyleDtoToInventoryStyle (InventoryStyleDto inventoryStyleDto);
    List<InventoryStyleDto> inventoryStylesToInventoryStyleDtos (List<InventoryStyle> inventoryStyles);
    List<InventoryStyle> inventoryStyleDtosToInventoryStyle (List<InventoryStyleDto> inventoryStyleDtos);
    
}
