package com.inventory_service.inventory_service.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

import com.inventory_service.inventory_service.dto.DamageLogDto;
import com.inventory_service.inventory_service.entity.DamageLog;

@Mapper (componentModel = "spring", uses={InventoryMapper.class})
public interface DamageLogMapper {

    
    
    DamageLogDto damageLogToDamageLogDto(DamageLog damageLog);
    @Mapping(target = "damageId",ignore = true)
    DamageLog damageLogDtoToDamageLog(DamageLogDto damageLogDto);
    


    
}
