package com.inventory_service.inventory_service.mapper;

import java.util.List;

import org.mapstruct.Mapper;

import com.inventory_service.inventory_service.dto.InventoryQuantityTrackDto;
import com.inventory_service.inventory_service.entity.InventoryQuantityTrack;

@Mapper(componentModel = "spring", uses={InventoryMapper.class})
public interface InventoryQuantityTrackMapper {
    InventoryQuantityTrackDto inventoryQuantityTrackToInventoryQuantityTrackDto (InventoryQuantityTrack inventoryQuantityTrack);
    InventoryQuantityTrack inventoryQuantityTrackDtoToInventoryQuantityTrack (InventoryQuantityTrackDto inventoryQuantityTrackDto);
    List <InventoryQuantityTrackDto > inventoryQuantityTracksToInventoryQuantityTrackDtos (List<InventoryQuantityTrack> inventoryQuantityTracks);
    List<InventoryQuantityTrack> inventoryQuantityTrackDtosToInventoryQuantityTracks (List<InventoryQuantityTrackDto> inventoryQuantityTrackDto);

    
} 