package com.inventory_service.inventory_service.service;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.inventory_service.inventory_service.dto.DamageAndQtyDto;
import com.inventory_service.inventory_service.dto.DamageLogDto;
import com.inventory_service.inventory_service.dto.InventoryDto;
import com.inventory_service.inventory_service.dto.ModelIdAndQtyAndDateDto;
import com.inventory_service.inventory_service.entity.DamageLog;
import com.inventory_service.inventory_service.entity.Inventory;
import com.inventory_service.inventory_service.exception.DamageNotFoundException;
import com.inventory_service.inventory_service.exception.ModelNotFoundException;
import com.inventory_service.inventory_service.mapper.DamageLogMapper;
import com.inventory_service.inventory_service.mapper.InventoryMapper;
import com.inventory_service.inventory_service.repository.DamageLogRepository;

import jakarta.transaction.Transactional;

@Service
public class DamageLogService {

    
    private final DamageLogMapper damageLogMapper;
    private final DamageLogRepository damageLogRepository;
    private final InventoryService inventoryService;
    private final InventoryMapper inventoryMapper;
    public DamageLogService(DamageLogMapper damageLogMapper, DamageLogRepository damageLogRepository, InventoryService inventoryService, InventoryMapper inventoryMapper) {
        this.inventoryService=inventoryService;
        this.damageLogMapper = damageLogMapper;
        this.damageLogRepository = damageLogRepository;
        this.inventoryMapper=inventoryMapper;
    }

    public void checkDamageId(Integer damageId){
        Optional<DamageLog> damageLog=damageLogRepository.findById(damageId);
        if(damageLog.isPresent());

    }
    
    public int getDamagedQty(String modelId, LocalDate targetDate){
        return damageLogRepository.getActiveDamagedQty(modelId, targetDate);
    }

    public Integer createDamage (String modelId, int qty, String reason) throws ModelNotFoundException{
        InventoryDto inventoryDto=inventoryService.getByModelId(modelId);
        Inventory inventory= inventoryMapper.inventoryDtoToInventory(inventoryDto);
        DamageLogDto damageLogDto= new DamageLogDto(null,inventory , qty, reason , LocalDate.now(), null);
        DamageLog damageLog=damageLogMapper.damageLogDtoToDamageLog(damageLogDto);
        damageLogRepository.save(damageLog);
        return damageLog.getDamageId();

    }

    @Transactional
    public void repairDamageByModels(List<ModelIdAndQtyAndDateDto> items) throws RuntimeException{
        for (ModelIdAndQtyAndDateDto item : items) {
            int remainingQty = item.getQty();
            List<DamageLog> activeLogs = damageLogRepository
                .findByModel_ModelIdAndDateRepairedIsNullOrderByDateAsc(item.getModelId());

            for (DamageLog log : activeLogs) {
                if (remainingQty <= 0) {
                    break;
                }

                int repairedQty = Math.min(log.getQuantity(), remainingQty);
                log.setQuantity(log.getQuantity() - repairedQty);
                remainingQty -= repairedQty;

                if (log.getQuantity() == 0) {
                    log.setDateRepaired(LocalDate.now());
                }
            }

            if (remainingQty > 0) {
                throw new RuntimeException("Unable to fully repair damage logs for modelId " + item.getModelId());
            }

            damageLogRepository.saveAll(activeLogs);
        }
    }

    @Transactional
    public void repairDamage(List<DamageAndQtyDto> damagedItems) throws RuntimeException{
        List<Integer> errors=new ArrayList<>();
        List<DamageLog> res= new ArrayList<>();
        for (DamageAndQtyDto damagedItem: damagedItems){
            Optional<DamageLog> damageLog=damageLogRepository.findById(damagedItem.getDamageId());
            if(damageLog.isPresent()){
                DamageLog curr=damageLog.get();
                if(curr.getQuantity()<damagedItem.getQuantity()){
                    errors.add(damagedItem.getDamageId());
                }
                else{
                    curr.setQuantity(curr.getQuantity()-damagedItem.getQuantity());
                    if(curr.getQuantity()==0){
                        curr.setDateRepaired(LocalDate.now());
                    }
                    res.add(curr);

                }
                
            }
            else{
                errors.add(damagedItem.getDamageId());
            }


        }
        if(errors.size()>0){
            throw new DamageNotFoundException(errors);
        }
        
        damageLogRepository.saveAll(res);



    }
        
        

}

    

    

