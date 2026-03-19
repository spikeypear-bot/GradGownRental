package com.inventory_service.inventory_service.service;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.inventory_service.inventory_service.dto.InventoryQuantityTrackDto;
import com.inventory_service.inventory_service.entity.InventoryQuantityTrack;
import com.inventory_service.inventory_service.entity.InventoryQuantityTrackId;
import com.inventory_service.inventory_service.mapper.InventoryQuantityTrackMapper;
import com.inventory_service.inventory_service.repository.InventoryQuantityTrackRepository;

@Service
public class InventoryQuantityTrackService {
    private final InventoryQuantityTrackRepository inventoryQuantityTrackRepository;
    private final InventoryQuantityTrackMapper inventoryQuantityTrackMapper;
    
    

    public InventoryQuantityTrackService(InventoryQuantityTrackRepository inventoryQuantityTrackRepository,
            InventoryQuantityTrackMapper inventoryQuantityTrackMapper) {
        this.inventoryQuantityTrackRepository = inventoryQuantityTrackRepository;
        this.inventoryQuantityTrackMapper = inventoryQuantityTrackMapper;
    }



    List<InventoryQuantityTrackDto> getListOfDatesWithQuantity(String modelId, LocalDate date){
        List<InventoryQuantityTrack> listOfDate=inventoryQuantityTrackRepository.getInventoryQuantityTrackByIdAfterDate(modelId, date);
        return inventoryQuantityTrackMapper.inventoryQuantityTracksToInventoryQuantityTrackDtos(listOfDate);

    }

    InventoryQuantityTrackDto getInventoryQuantityTrackByDate(String modelId,LocalDate date){
        Optional<InventoryQuantityTrack> inventoryQuantityTrack= inventoryQuantityTrackRepository.findById(new InventoryQuantityTrackId(modelId, date));
        if (inventoryQuantityTrack.isPresent()){
            return inventoryQuantityTrackMapper.inventoryQuantityTrackToInventoryQuantityTrackDto(inventoryQuantityTrack.get());
        
        }
        else{
            return null;
        }
    }
    




    
    


    
}
