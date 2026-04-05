package com.inventory_service.inventory_service.service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import java.util.UUID;

import org.springframework.stereotype.Service;

import com.inventory_service.inventory_service.dto.DamageAndQtyDto;
import com.inventory_service.inventory_service.dto.InventoryDateAndQuantityDto;
import com.inventory_service.inventory_service.dto.InventoryDto;
import com.inventory_service.inventory_service.dto.InventoryQuantityTrackDto;
import com.inventory_service.inventory_service.dto.ItemAndDamageIdDto;
import com.inventory_service.inventory_service.dto.ItemHoldDto;
import com.inventory_service.inventory_service.dto.ModelIdAndQtyAndDateDto;
import com.inventory_service.inventory_service.dto.ReserveDto;
import com.inventory_service.inventory_service.dto.SoftHoldDto;
import com.inventory_service.inventory_service.entity.Inventory;
import com.inventory_service.inventory_service.entity.InventoryQuantityTrack;
import com.inventory_service.inventory_service.exception.DamageNotFoundException;
import com.inventory_service.inventory_service.exception.ModelNotFoundException;
import com.inventory_service.inventory_service.mapper.InventoryMapper;
import com.inventory_service.inventory_service.mapper.InventoryQuantityTrackMapper;
import com.inventory_service.inventory_service.repository.InventoryQuantityTrackRepository;
import com.inventory_service.inventory_service.repository.ItemHoldRepository;

import jakarta.transaction.Transactional;

@Service
public class PostService {
    private final DamageLogService damageLogService;
    private final InventoryService inventoryService;
    private final GetService getService;
    private final InventoryQuantityTrackService inventoryQuantityTrackService;
    private final InventoryMapper inventoryMapper;
    private final ItemHoldService itemHoldService;
    private final InventoryQuantityTrackRepository inventoryQuantityTrackRepository;
    private final InventoryQuantityTrackMapper inventoryQuantityTrackMapper;
    private final ItemHoldRepository itemHoldRepository;

    public PostService(InventoryService inventoryService, GetService getService,
            InventoryQuantityTrackService inventoryQuantityTrackService,InventoryMapper inventoryMapper,ItemHoldService itemHoldService,InventoryQuantityTrackRepository inventoryQuantityTrackRepository,InventoryQuantityTrackMapper inventoryQuantityTrackMapper,
        ItemHoldRepository itemHoldRepository,DamageLogService damageLogService) {
        this.inventoryService = inventoryService;
        this.getService = getService;
        this.inventoryQuantityTrackService = inventoryQuantityTrackService;
        this.itemHoldService=itemHoldService;
        this.inventoryMapper=inventoryMapper;
        this.inventoryQuantityTrackRepository=inventoryQuantityTrackRepository;
        this.inventoryQuantityTrackMapper=inventoryQuantityTrackMapper;
        this.itemHoldRepository=itemHoldRepository;
        this.damageLogService=damageLogService; 
    }





    @Transactional
    public SoftHoldDto makeSoftHold (List<ModelIdAndQtyAndDateDto> items) throws RuntimeException,ModelNotFoundException{
        


        for(ModelIdAndQtyAndDateDto item: items){
            LocalDate chosenDate=item.getChosenDate();

            InventoryDto itemDto=inventoryService.getByModelId(item.getModelId());
            for(int i=0;i<7;i++){
                LocalDate curr=chosenDate.plusDays(i);
                InventoryDateAndQuantityDto check=getService.getInventoryAvailableDateAndQuantity(itemDto, curr);
                if(check.getAvailableQty()<item.getQty()){
                     
                    throw new RuntimeException("Not able to soft-hold, as there is not enough qty of selected items.");
                }

            }

        }
        UUID uuid = UUID.randomUUID();
        String holdId=uuid.toString();
        LocalDateTime createdAt=LocalDateTime.now();

        List<ItemHoldDto> res= new ArrayList<>();

        for(ModelIdAndQtyAndDateDto item:items){
            InventoryDto itemDto=inventoryService.getByModelId(item.getModelId());
            Inventory itemMapped=inventoryMapper.inventoryDtoToInventory(itemDto);
            res.add(new ItemHoldDto(holdId,itemMapped,item.getQty(),item.getChosenDate(),createdAt));





        }
        itemHoldService.setAllItems(res);
        
        return new SoftHoldDto(holdId,items,createdAt);

    }

    @Transactional
    public void dbMakeItemsReserve(String modelId,int qty,LocalDate date) throws ModelNotFoundException{
        InventoryDto itemDto=inventoryService.getByModelId(modelId);
        Inventory itemMapped=inventoryMapper.inventoryDtoToInventory(itemDto);
        inventoryQuantityTrackRepository.save(
            new InventoryQuantityTrack(
                date,
                itemMapped,
                qty,
                0,
                0,
                InventoryQuantityTrackService.DEFAULT_BACKUP_QTY
            )
        );

    }
    
    @Transactional
    public void reserveItems(ReserveDto reserveDto) throws RuntimeException,ModelNotFoundException{
        List<ModelIdAndQtyAndDateDto> items=reserveDto.getItems();
        
        
        for(ModelIdAndQtyAndDateDto item: items){
            LocalDate chosenDate=item.getChosenDate();

            InventoryDto itemDto=inventoryService.getByModelId(item.getModelId());
            for(int i=0;i<7;i++){
                
                LocalDate curr=chosenDate.plusDays(i);
                InventoryDateAndQuantityDto check=getService.getInventoryAvailableDateAndQuantity(itemDto, curr);
                if(check.getAvailableQty()<item.getQty()){
                    throw new RuntimeException("Not able to purchase items, as there is not enough qty of selected items.");
                }

            }

        }

        
        for(ModelIdAndQtyAndDateDto item:items){
            LocalDate chosenDate=item.getChosenDate();
            InventoryDto itemDto=inventoryService.getByModelId(item.getModelId());
            for(int i=0;i<7;i++){
                LocalDate curr=chosenDate.plusDays(i);
                InventoryQuantityTrackDto inventoryQuantityTrackDto=inventoryQuantityTrackService.getInventoryQuantityTrackByDate(itemDto.getModelId(), curr);
                if(inventoryQuantityTrackDto==null){
                    dbMakeItemsReserve(item.getModelId(),item.getQty() , curr);

                }
                else{
                    int a= inventoryQuantityTrackDto.getReservedQty();
                    inventoryQuantityTrackDto.setReservedQty(a+item.getQty());
                    inventoryQuantityTrackRepository.save(inventoryQuantityTrackMapper.inventoryQuantityTrackDtoToInventoryQuantityTrack(inventoryQuantityTrackDto));


                }

            }

        }
        itemHoldRepository.deleteAllByHoldId(reserveDto.getHoldId());


    }

    private InventoryQuantityTrackDto getOrCreateTrackSnapshot(String modelId, LocalDate targetDate) throws ModelNotFoundException {
        InventoryQuantityTrackDto exactTrack = inventoryQuantityTrackService.getInventoryQuantityTrackByDate(modelId, targetDate);
        if (exactTrack != null) {
            return exactTrack;
        }

        InventoryDto itemDto = inventoryService.getByModelId(modelId);
        Inventory itemMapped = inventoryMapper.inventoryDtoToInventory(itemDto);

        InventoryQuantityTrack snapshot = inventoryQuantityTrackRepository
            .findFirstByModel_ModelIdAndDateLessThanEqualOrderByDateDesc(modelId, targetDate)
            .orElse(null);

        if (snapshot == null) {
            return new InventoryQuantityTrackDto(
                targetDate,
                itemMapped,
                0,
                0,
                0,
                0,
                InventoryQuantityTrackService.DEFAULT_BACKUP_QTY
            );
        }

        return new InventoryQuantityTrackDto(
            targetDate,
            itemMapped,
            snapshot.getAvailableQty(),
            snapshot.getReservedQty(),
            snapshot.getRentedQty(),
            snapshot.getWashQty(),
            inventoryQuantityTrackService.resolveBackupQty(snapshot.getBackupQty())
        );
    }

    private void applyTrackAdjustment(String modelId, LocalDate targetDate, Consumer<InventoryQuantityTrackDto> adjuster)
        throws ModelNotFoundException {
        InventoryQuantityTrackDto trackDto = getOrCreateTrackSnapshot(modelId, targetDate);
        adjuster.accept(trackDto);
        inventoryQuantityTrackRepository.save(
            inventoryQuantityTrackMapper.inventoryQuantityTrackDtoToInventoryQuantityTrack(trackDto)
        );
    }

    private InventoryQuantityTrackDto requireExistingTrack(String modelId, LocalDate targetDate, String transition)
        throws ModelNotFoundException {
        InventoryQuantityTrackDto trackDto =
            inventoryQuantityTrackService.getInventoryQuantityTrackByDate(modelId, targetDate);
        if (trackDto == null) {
            throw new RuntimeException(
                String.format(
                    "Cannot apply %s for modelId=%s on date=%s because no inventory track exists.",
                    transition,
                    modelId,
                    targetDate
                )
            );
        }
        return trackDto;
    }

    private int getRemainingWindowDays(LocalDate chosenDate) {
        LocalDate today = LocalDate.now();
        if (today.isBefore(chosenDate)) {
            return 7;
        }
        long daysDiff = ChronoUnit.DAYS.between(chosenDate, today);
        return Math.max(7 - (int) daysDiff, 0);
    }

    private LocalDate getTransitionStartDate(LocalDate chosenDate) {
        LocalDate today = LocalDate.now();
        return today.isAfter(chosenDate) ? today : chosenDate;
    }
    @Transactional
    public void collectItems(List<ModelIdAndQtyAndDateDto> items) throws ModelNotFoundException{
        
        for(ModelIdAndQtyAndDateDto item:items){
            LocalDate chosenDate=item.getChosenDate();
            InventoryDto itemDto=inventoryService.getByModelId(item.getModelId());
            for(int i=0;i<7;i++){
                
                LocalDate curr=chosenDate.plusDays(i);
                InventoryQuantityTrackDto inventoryQuantityTrackDto =
                    requireExistingTrack(itemDto.getModelId(), curr, "RESERVED_TO_RENTED");
                int a= inventoryQuantityTrackDto.getReservedQty();
                if (a < item.getQty()) {
                    throw new RuntimeException(
                        String.format(
                            "Cannot apply RESERVED_TO_RENTED for modelId=%s on date=%s because reserved_qty=%d is less than requested qty=%d.",
                            itemDto.getModelId(),
                            curr,
                            a,
                            item.getQty()
                        )
                    );
                }
                inventoryQuantityTrackDto.setReservedQty(a-item.getQty());
                int b= inventoryQuantityTrackDto.getRentedQty();
                inventoryQuantityTrackDto.setRentedQty(b+item.getQty());
                inventoryQuantityTrackRepository.save(inventoryQuantityTrackMapper.inventoryQuantityTrackDtoToInventoryQuantityTrack(inventoryQuantityTrackDto));


            
            }
        }



    }
    
    @Transactional
    public void washItems(List<ModelIdAndQtyAndDateDto> items) throws ModelNotFoundException{
        
        for(ModelIdAndQtyAndDateDto item:items){
            LocalDate startDate = getTransitionStartDate(item.getChosenDate());
            int remainingDays = getRemainingWindowDays(item.getChosenDate());

            InventoryDto itemDto=inventoryService.getByModelId(item.getModelId());

            for(int i=0;i<remainingDays;i++){
                
                LocalDate curr=startDate.plusDays(i);
                InventoryQuantityTrackDto inventoryQuantityTrackDto =
                    requireExistingTrack(itemDto.getModelId(), curr, "RENTED_TO_WASH");
                int a= inventoryQuantityTrackDto.getRentedQty();
                if (a < item.getQty()) {
                    throw new RuntimeException(
                        String.format(
                            "Cannot apply RENTED_TO_WASH for modelId=%s on date=%s because rented_qty=%d is less than requested qty=%d.",
                            itemDto.getModelId(),
                            curr,
                            a,
                            item.getQty()
                        )
                    );
                }
                inventoryQuantityTrackDto.setRentedQty(a-item.getQty());
                int b= inventoryQuantityTrackDto.getWashQty();
                inventoryQuantityTrackDto.setWashQty(b+item.getQty());
                inventoryQuantityTrackRepository.save(inventoryQuantityTrackMapper.inventoryQuantityTrackDtoToInventoryQuantityTrack(inventoryQuantityTrackDto));


            
            }
        }



    }

    @Transactional
    public List<ItemAndDamageIdDto> damageItems(List<ModelIdAndQtyAndDateDto> items) throws ModelNotFoundException{
        List<ItemAndDamageIdDto> itemAndDamageIdDtos=new ArrayList<>();
        
        
        for(ModelIdAndQtyAndDateDto item:items){
            LocalDate startDate = getTransitionStartDate(item.getChosenDate());
            int remainingDays = getRemainingWindowDays(item.getChosenDate());
            Integer damageId= damageLogService.createDamage(item.getModelId(),item.getQty(),null);
            itemAndDamageIdDtos.add(new ItemAndDamageIdDto(damageId,item));
            InventoryDto itemDto=inventoryService.getByModelId(item.getModelId());
            for(int i=0;i<remainingDays;i++){

                LocalDate curr=startDate.plusDays(i);
                InventoryQuantityTrackDto inventoryQuantityTrackDto =
                    requireExistingTrack(itemDto.getModelId(), curr, "RENTED_TO_DAMAGED");
                int rentedQty= inventoryQuantityTrackDto.getRentedQty();
                if (rentedQty < item.getQty()) {
                    throw new RuntimeException(
                        String.format(
                            "Cannot apply RENTED_TO_DAMAGED for modelId=%s on date=%s because rented_qty=%d is less than requested qty=%d.",
                            itemDto.getModelId(),
                            curr,
                            rentedQty,
                            item.getQty()
                        )
                    );
                }
                inventoryQuantityTrackDto.setRentedQty(rentedQty-item.getQty());
                
                inventoryQuantityTrackRepository.save(inventoryQuantityTrackMapper.inventoryQuantityTrackDtoToInventoryQuantityTrack(inventoryQuantityTrackDto));


            
            }
            
        }
        return itemAndDamageIdDtos;



    }

    @Transactional
    public void moveDamagedToRepair(List<ModelIdAndQtyAndDateDto> items) throws ModelNotFoundException{
        // Damaged stock is tracked through DamageLog. No inventoryquantitytrack
        // bucket updates are needed for the repair stage.
    }

    @Transactional
    public void moveRepairToWash(List<ModelIdAndQtyAndDateDto> items) throws ModelNotFoundException{
        for (ModelIdAndQtyAndDateDto item : items) {
            LocalDate startDate = getTransitionStartDate(item.getChosenDate());
            int remainingDays = getRemainingWindowDays(item.getChosenDate());
            for (int i = 0; i < remainingDays; i++) {
                LocalDate targetDate = startDate.plusDays(i);
                applyTrackAdjustment(item.getModelId(), targetDate, trackDto -> {
                    trackDto.setWashQty(trackDto.getWashQty() + item.getQty());
                });
            }
        }
        damageLogService.repairDamageByModels(items);
    }

    @Transactional
    public void moveWashToAvailable(List<ModelIdAndQtyAndDateDto> items) throws ModelNotFoundException{
        for (ModelIdAndQtyAndDateDto item : items) {
            LocalDate startDate = getTransitionStartDate(item.getChosenDate());
            int remainingDays = getRemainingWindowDays(item.getChosenDate());
            for (int i = 0; i < remainingDays; i++) {
                LocalDate targetDate = startDate.plusDays(i);
                applyTrackAdjustment(item.getModelId(), targetDate, trackDto -> {
                    trackDto.setWashQty(Math.max(trackDto.getWashQty() - item.getQty(), 0));
                });
            }
        }
    }

    
    @Transactional
    public void repairItems( List<DamageAndQtyDto> repairedList) throws DamageNotFoundException{
       
        damageLogService.repairDamage(repairedList);

    }






    
}
