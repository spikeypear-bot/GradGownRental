package com.inventory_service.inventory_service.service;

import java.time.Duration;
import java.time.LocalDate;
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
    private static final Duration HOLD_EXPIRY = Duration.ofMinutes(10);

    private final ItemHoldMapper itemHoldMapper;
    private final ItemHoldRepository itemHoldRepository;

    public ItemHoldService(ItemHoldMapper itemHoldMapper, ItemHoldRepository itemHoldRepository) {
        this.itemHoldMapper = itemHoldMapper;
        this.itemHoldRepository = itemHoldRepository;
    }

    // Get all holds for this model_id
    public List<ItemHoldDto> getAllItemHoldByModel(String modelId) {
        purgeExpiredHolds();
        List<ItemHold> itemHolds = itemHoldRepository.findAllByModel_ModelId(modelId);
        return itemHoldMapper.itemHoldsToItemHoldDtos(itemHolds);
    }

    // Get all non-expired holds for this model_id
    public List<ItemHoldDto> getAllNonExpiredItemHold(String modelId) {
        purgeExpiredHolds();
        List<ItemHold> itemHolds = itemHoldRepository.findAllByModel_ModelId(modelId);
        List<ItemHold> nonExpiredHolds = new ArrayList<>();
        LocalDateTime cutoff = LocalDateTime.now().minus(HOLD_EXPIRY);
        for (ItemHold itemHold : itemHolds) {
            LocalDateTime createdTime = itemHold.getCreatedAt();
            if (createdTime != null && createdTime.isAfter(cutoff)) {
                nonExpiredHolds.add(itemHold);
            }

        }
        return itemHoldMapper.itemHoldsToItemHoldDtos(nonExpiredHolds);

    }

    public List<ItemHoldDto> getActiveItemHoldForDate(String modelId, LocalDate date) {
        List<ItemHoldDto> nonExpiredHolds = getAllNonExpiredItemHold(modelId);
        List<ItemHoldDto> activeHolds = new ArrayList<>();
        for (ItemHoldDto itemHoldDto : nonExpiredHolds) {
            LocalDate chosenDate = itemHoldDto.getChosenDate();
            if (chosenDate == null) {
                continue;
            }
            LocalDate endDateExclusive = chosenDate.plusDays(7);
            if (!date.isBefore(chosenDate) && date.isBefore(endDateExclusive)) {
                activeHolds.add(itemHoldDto);
            }
        }
        return activeHolds;
    }

    @Transactional
    public void setItem(ItemHoldDto itemHoldDto) {
        purgeExpiredHolds();
        itemHoldRepository.save(itemHoldMapper.itemHoldDtoToItemHold(itemHoldDto));

    }
    @Transactional
    public void setAllItems(List<ItemHoldDto> itemHoldDtos) {
        purgeExpiredHolds();
        itemHoldRepository.saveAll(itemHoldMapper.itemHoldDtosToItemHolds(itemHoldDtos));
    }

    @Transactional
    public void purgeExpiredHolds() {
        LocalDateTime cutoff = LocalDateTime.now().minus(HOLD_EXPIRY);
        itemHoldRepository.deleteAllByCreatedAtBefore(cutoff);
    }

}
