package com.inventory_service.inventory_service.service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;

import com.inventory_service.inventory_service.dto.InventoryDateAndQuantityDto;
import com.inventory_service.inventory_service.dto.InventoryDto;
import com.inventory_service.inventory_service.dto.InventoryQuantityTrackDto;
import com.inventory_service.inventory_service.dto.ItemHoldDto;
import com.inventory_service.inventory_service.dto.ModelIdAndQtyAndDateDto;
import com.inventory_service.inventory_service.dto.ReserveDto;
import com.inventory_service.inventory_service.dto.SoftHoldDto;
import com.inventory_service.inventory_service.entity.Inventory;
import com.inventory_service.inventory_service.entity.InventoryQuantityTrack;
import com.inventory_service.inventory_service.mapper.InventoryMapper;
import com.inventory_service.inventory_service.mapper.InventoryQuantityTrackMapper;
import com.inventory_service.inventory_service.repository.InventoryQuantityTrackRepository;
import com.inventory_service.inventory_service.repository.ItemHoldRepository;

import jakarta.transaction.Transactional;

@Service
public class PostService {
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
        ItemHoldRepository itemHoldRepository) {
        this.inventoryService = inventoryService;
        this.getService = getService;
        this.inventoryQuantityTrackService = inventoryQuantityTrackService;
        this.itemHoldService=itemHoldService;
        this.inventoryMapper=inventoryMapper;
        this.inventoryQuantityTrackRepository=inventoryQuantityTrackRepository;
        this.inventoryQuantityTrackMapper=inventoryQuantityTrackMapper;
        this.itemHoldRepository=itemHoldRepository;
    }





    @Transactional
    public SoftHoldDto makeSoftHold (List<ModelIdAndQtyAndDateDto> items) throws RuntimeException{
        


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
            res.add(new ItemHoldDto(holdId,itemMapped,item.getQty(),createdAt));





        }
        itemHoldService.setAllItems(res);
        
        return new SoftHoldDto(holdId,items,createdAt);

    }

    @Transactional
    public void dbMakeItemsReserve(String modelId,int qty,LocalDate date) throws RuntimeException{
        InventoryDto itemDto=inventoryService.getByModelId(modelId);
        Inventory itemMapped=inventoryMapper.inventoryDtoToInventory(itemDto);
        inventoryQuantityTrackRepository.save(new InventoryQuantityTrack(date,itemMapped,qty,0,0,0,10));

    }
    
    @Transactional
    public void reserveItems(ReserveDto reserveDto) throws RuntimeException{
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
    @Transactional
    public void collectItems(List<ModelIdAndQtyAndDateDto> items) throws RuntimeException{
        
        for(ModelIdAndQtyAndDateDto item:items){
            LocalDate chosenDate=item.getChosenDate();
            InventoryDto itemDto=inventoryService.getByModelId(item.getModelId());
            for(int i=0;i<7;i++){
                
                LocalDate curr=chosenDate.plusDays(i);
                InventoryQuantityTrackDto inventoryQuantityTrackDto=inventoryQuantityTrackService.getInventoryQuantityTrackByDate(itemDto.getModelId(), curr);
                int a= inventoryQuantityTrackDto.getReservedQty();
                inventoryQuantityTrackDto.setReservedQty(a-item.getQty());
                int b= inventoryQuantityTrackDto.getRentedQty();
                inventoryQuantityTrackDto.setRentedQty(b+item.getQty());
                inventoryQuantityTrackRepository.save(inventoryQuantityTrackMapper.inventoryQuantityTrackDtoToInventoryQuantityTrack(inventoryQuantityTrackDto));


            
            }
        }



    }
    
    @Transactional
    public void washItems(List<ModelIdAndQtyAndDateDto> items) throws RuntimeException{
        
        for(ModelIdAndQtyAndDateDto item:items){
            LocalDate chosenDate=item.getChosenDate();
            LocalDate today=LocalDate.now();
            long daysDiff = ChronoUnit.DAYS.between(today, chosenDate);
            int daysDiff2=7-(int) daysDiff;

            InventoryDto itemDto=inventoryService.getByModelId(item.getModelId());

            for(int i=0;i<daysDiff2;i++){
                
                LocalDate curr=today.plusDays(i);
                InventoryQuantityTrackDto inventoryQuantityTrackDto=inventoryQuantityTrackService.getInventoryQuantityTrackByDate(itemDto.getModelId(), curr);
                int a= inventoryQuantityTrackDto.getRentedQty();
                inventoryQuantityTrackDto.setRentedQty(a-item.getQty());
                int b= inventoryQuantityTrackDto.getWashQty();
                inventoryQuantityTrackDto.setWashQty(b+item.getQty());
                inventoryQuantityTrackRepository.save(inventoryQuantityTrackMapper.inventoryQuantityTrackDtoToInventoryQuantityTrack(inventoryQuantityTrackDto));


            
            }
        }



    }

    @Transactional
    public void damagedItems(ReserveDto reserveDto) throws RuntimeException{
        
        List<ModelIdAndQtyAndDateDto> items=reserveDto.getItems();
        
        for(ModelIdAndQtyAndDateDto item:items){
            LocalDate chosenDate=item.getChosenDate();
            LocalDate today=LocalDate.now();
            long daysDiff = ChronoUnit.DAYS.between(today, chosenDate);
            int daysDiff2=7-(int) daysDiff;

            
            InventoryDto itemDto=inventoryService.getByModelId(item.getModelId());
            for(int i=0;i<daysDiff2;i++){

                LocalDate curr=chosenDate.plusDays(i);
                InventoryQuantityTrackDto inventoryQuantityTrackDto=inventoryQuantityTrackService.getInventoryQuantityTrackByDate(itemDto.getModelId(), curr);
                int a= inventoryQuantityTrackDto.getReservedQty();
                inventoryQuantityTrackDto.setRentedQty(a-item.getQty());
                inventoryQuantityTrackDto.setWashQty(a+item.getQty());
                inventoryQuantityTrackRepository.save(inventoryQuantityTrackMapper.inventoryQuantityTrackDtoToInventoryQuantityTrack(inventoryQuantityTrackDto));


            
            }
        }



    }






    
}
