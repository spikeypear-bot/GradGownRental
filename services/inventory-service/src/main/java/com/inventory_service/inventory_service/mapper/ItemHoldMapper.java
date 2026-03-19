package com.inventory_service.inventory_service.mapper;

import java.util.List;

import org.mapstruct.Mapper;

import com.inventory_service.inventory_service.dto.ItemHoldDto;
import com.inventory_service.inventory_service.entity.ItemHold;

@Mapper(componentModel = "spring",uses = {InventoryMapper.class})
public interface ItemHoldMapper  {
    ItemHoldDto itemHoldToItemHoldDto (ItemHold itemHold);
    ItemHold itemHoldDtoToItemHold ( ItemHoldDto itemHoldDto);
    List<ItemHoldDto> itemHoldsToItemHoldDtos (List<ItemHold> itemHolds);
    List<ItemHold> itemHoldDtosToItemHolds ( List<ItemHoldDto> itemHoldDtos);


    
}
