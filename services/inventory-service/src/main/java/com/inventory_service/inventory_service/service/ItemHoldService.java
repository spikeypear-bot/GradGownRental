package com.inventory_service.inventory_service.service;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Service;

import com.inventory_service.inventory_service.dto.ItemHoldDto;
import com.inventory_service.inventory_service.entity.ItemHold;
import com.inventory_service.inventory_service.mapper.ItemHoldMapper;
import com.inventory_service.inventory_service.repository.ItemHoldRepository;

import jakarta.transaction.Transactional;

@Service
public class ItemHoldService {
    private final ItemHoldMapper itemHoldMapper;
    private final ItemHoldRepository itemHoldRepository;

    public ItemHoldService(ItemHoldMapper itemHoldMapper, ItemHoldRepository itemHoldRepository) {
        this.itemHoldMapper = itemHoldMapper;
        this.itemHoldRepository = itemHoldRepository;
    }

    // Get all holds for this model_id
    public List<ItemHoldDto> getAllItemHoldByModel(String modelId) {
        List<ItemHold> itemHolds = itemHoldRepository.findAllByModel_ModelId(modelId);
        return itemHoldMapper.itemHoldsToItemHoldDtos(itemHolds);
    }

    // Get all non-expired holds for this model_id
    public List<ItemHoldDto> getAllNonExpiredItemHold(String modelId) {
        List<ItemHold> itemHolds = itemHoldRepository.findAllByModel_ModelId(modelId);
        List<ItemHold> nonExpiredHolds = new ArrayList<>();
        LocalDateTime currentTime = LocalDateTime.now();
        for (ItemHold itemHold : itemHolds) {
            LocalDateTime createdTime = itemHold.getCreatedAt();
            Duration duration = Duration.between(createdTime, currentTime);
            if (duration.toMinutes() <= 10) {
                nonExpiredHolds.add(itemHold);
            }

        }
        return itemHoldMapper.itemHoldsToItemHoldDtos(nonExpiredHolds);

    }

    @Transactional
    public void setItem(ItemHoldDto itemHoldDto) {
        itemHoldRepository.save(itemHoldMapper.itemHoldDtoToItemHold(itemHoldDto));

    }
    @Transactional
    public void setAllItems(List<ItemHoldDto> itemHoldDtos) {
        itemHoldRepository.saveAll(itemHoldMapper.itemHoldDtosToItemHolds(itemHoldDtos));
    }

}
