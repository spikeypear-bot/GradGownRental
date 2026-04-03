package com.inventory_service.inventory_service.service;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.inventory_service.inventory_service.dto.InventoryQuantityTrackDto;
import com.inventory_service.inventory_service.dto.StockOverviewRowDto;
import com.inventory_service.inventory_service.entity.Inventory;
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

    public List<StockOverviewRowDto> getStockOverviewRows(LocalDate date, List<Inventory> inventoryList) {
        Map<String, InventoryQuantityTrack> latestTrackByModelId = new HashMap<>();
        for (InventoryQuantityTrack track : inventoryQuantityTrackRepository.getLatestInventoryQuantityTrackForDate(date)) {
            latestTrackByModelId.put(track.getModel().getModelId(), track);
        }

        return inventoryList.stream().map(inventory -> {
            InventoryQuantityTrack track = latestTrackByModelId.get(inventory.getModelId());
            int reservedQty = track != null ? track.getReservedQty() : 0;
            int rentedQty = track != null ? track.getRentedQty() : 0;
            int damagedQty = track != null ? track.getDamagedQty() : 0;
            int repairQty = track != null ? track.getRepairQty() : 0;
            int washQty = track != null ? track.getWashQty() : 0;
            int backupQty = track != null ? track.getBackupQty() : 0;
            int availableQty = track != null
                ? track.getAvailableQty()
                : Math.max(inventory.getTotalQty() - reservedQty - rentedQty - damagedQty - repairQty - washQty, 0);

            return new StockOverviewRowDto(
                inventory.getModelId(),
                inventory.getStyle() != null ? inventory.getStyle().getItemName() : "Unknown Item",
                inventory.getStyle() != null ? inventory.getStyle().getItemType() : "item",
                inventory.getSize(),
                inventory.getTotalQty(),
                availableQty,
                reservedQty,
                rentedQty,
                damagedQty,
                repairQty,
                washQty,
                backupQty
            );
        }).toList();
    }




    
    


    
}
