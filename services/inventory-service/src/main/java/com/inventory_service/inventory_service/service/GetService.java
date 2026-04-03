package com.inventory_service.inventory_service.service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Service;

import com.inventory_service.inventory_service.dto.ComponentAvailabilityDto;
import com.inventory_service.inventory_service.dto.DailyAvailabilityDto;
import com.inventory_service.inventory_service.dto.GraduationPackageDto;
import com.inventory_service.inventory_service.dto.InventoryDateAndQuantityDto;
import com.inventory_service.inventory_service.dto.InventoryDto;
import com.inventory_service.inventory_service.dto.InventoryQuantityTrackDto;
import com.inventory_service.inventory_service.dto.InventoryStyleDto;
import com.inventory_service.inventory_service.dto.ItemHoldDto;
import com.inventory_service.inventory_service.dto.ModelOnlyDto;
import com.inventory_service.inventory_service.dto.PackageWithPriceDto;
import com.inventory_service.inventory_service.dto.PackageWithStyleAndInventoryDto;
import com.inventory_service.inventory_service.dto.StockOverviewRowDto;
import com.inventory_service.inventory_service.dto.StyleWithInventoryDto;
import com.inventory_service.inventory_service.exception.ModelNotFoundException;
import com.inventory_service.inventory_service.exception.PackageNotFoundException;


@Service
public class GetService {
    private final InventoryService inventoryService;
    private final DamageLogService damageLogService;
    
    private final InventoryQuantityTrackService inventoryQuantityTrackService;
    private final GraduationPackageService graduationPackageService;
    private final ItemHoldService itemHoldService;
    public GetService(InventoryService inventoryService,
            InventoryQuantityTrackService inventoryQuantityTrackService,
            GraduationPackageService graduationPackageService,ItemHoldService itemHoldService,DamageLogService damageLogService) {
        this.inventoryService = inventoryService;
        this.damageLogService=damageLogService;
        this.inventoryQuantityTrackService = inventoryQuantityTrackService;
        this.graduationPackageService = graduationPackageService;
        this.itemHoldService=itemHoldService;
    }

    
    // Intermediate methods//
    // Calculate total rental fees based on a graduation package.
    public BigDecimal calculateTotalRentalFee (GraduationPackageDto graduationPackageDto){
        InventoryStyleDto hatStyle = graduationPackageDto.getHatStyle();
            InventoryStyleDto gownStyle= graduationPackageDto.getGownStyle();
            InventoryStyleDto hoodStyle=graduationPackageDto.getHoodStyle();
            BigDecimal totalRentalFee=new BigDecimal(0);
            
            if (hatStyle!=null){
                totalRentalFee=totalRentalFee.add(hatStyle.getRentalFee());
                

            }
            if (gownStyle!=null){
                totalRentalFee=totalRentalFee.add(gownStyle.getRentalFee());
                

            }
            if (hoodStyle!=null){
                totalRentalFee=totalRentalFee.add(hoodStyle.getRentalFee());
                

            }
            return totalRentalFee;
    }
    // Calculate total deposits based on a graduation package

    public BigDecimal calculateTotalDeposit (GraduationPackageDto graduationPackageDto){
        InventoryStyleDto hatStyle = graduationPackageDto.getHatStyle();
            InventoryStyleDto gownStyle= graduationPackageDto.getGownStyle();
            InventoryStyleDto hoodStyle=graduationPackageDto.getHoodStyle();
            BigDecimal totalDeposit=new BigDecimal(0);
            
            if (hatStyle!=null){
                totalDeposit=totalDeposit.add(hatStyle.getDeposit());
                

            }
            if (gownStyle!=null){
                totalDeposit=totalDeposit.add(gownStyle.getDeposit());
                

            }
            if (hoodStyle!=null){
                totalDeposit=totalDeposit.add(hoodStyle.getDeposit());
                

            }
            return totalDeposit;
    }
    
    //Get all inventory by style, so based on one style map out all the models

    public StyleWithInventoryDto getAllInventoryDtoByStyle(InventoryStyleDto inventoryStyleDto){
        if(inventoryStyleDto==null){
            return null;
        }
        
        List<InventoryDto> inventoryDtos= inventoryService.getInventoryByStyleId(inventoryStyleDto.getStyleId());
        List<ModelOnlyDto> modelOnlyDtos=new ArrayList<>();

        for(InventoryDto i: inventoryDtos){
            modelOnlyDtos.add(new ModelOnlyDto(i.getModelId(),i.getSize(),i.getTotalQty()));

        }
        StyleWithInventoryDto res= new StyleWithInventoryDto(inventoryStyleDto, modelOnlyDtos);

        return res;
        


    }
    //Major functions//

    // Get all packages with pricing//
    public List<PackageWithPriceDto> getAllPackagesWithPricing(){
        List<PackageWithPriceDto> res= new ArrayList<>();
        List<GraduationPackageDto> graduationPackageDtos= graduationPackageService.getAllGraduationPackages();
        for(GraduationPackageDto graduationPackageDto:  graduationPackageDtos){
            
            BigDecimal totalRentalFee=calculateTotalDeposit(graduationPackageDto);
            BigDecimal totalDeposit=calculateTotalRentalFee(graduationPackageDto);
            BigDecimal totalPrice=totalRentalFee.add(totalDeposit);
            PackageWithPriceDto temp=new PackageWithPriceDto(graduationPackageDto,totalDeposit,totalRentalFee,totalPrice);
            res.add(temp);
            
        }
        return res;
        

    }

    // Get all packages based on the institution, education level and faculty selected. 

    public List<PackageWithPriceDto> getAllPackagesMatched(String educationLevel,String faculty,String institution){
        List<PackageWithPriceDto> res= new ArrayList<>();
        List<GraduationPackageDto> graduationPackageDtos= graduationPackageService.getGraduationPackageByEducationLevelAndInstitutionAndFaculty(educationLevel, institution, faculty);
        for(GraduationPackageDto graduationPackageDto:  graduationPackageDtos){
            
            BigDecimal totalRentalFee=calculateTotalDeposit(graduationPackageDto);
            BigDecimal totalDeposit=calculateTotalRentalFee(graduationPackageDto);
            BigDecimal totalPrice=totalRentalFee.add(totalDeposit);
            PackageWithPriceDto temp=new PackageWithPriceDto(graduationPackageDto,totalDeposit,totalRentalFee,totalPrice);
            res.add(temp);
            
        }
        return res;

    }

    public List<StockOverviewRowDto> getStockOverview(LocalDate date){
        return inventoryQuantityTrackService.getStockOverviewRows(date, inventoryService.getAllInventoryEntity());
    }

    //Get all packages, showing the styles and the sizes they offer//

    public PackageWithStyleAndInventoryDto getPackageWithStyleAndInventory(int packageId) throws PackageNotFoundException{
        //Making elements for the constructors
        GraduationPackageDto graduationPackageDto=graduationPackageService.getByPackageId(packageId);
        InventoryStyleDto hatStyleDto=graduationPackageDto.getHatStyle();
        StyleWithInventoryDto hatStyleWithInventoryDto = getAllInventoryDtoByStyle(hatStyleDto);
        InventoryStyleDto gownStyleDto=graduationPackageDto.getGownStyle();
        StyleWithInventoryDto gownStyleWithInventoryDto=getAllInventoryDtoByStyle(gownStyleDto);
        InventoryStyleDto hoodStyleDto=graduationPackageDto.getHoodStyle();
        StyleWithInventoryDto hoodStyleWithInventoryDto=getAllInventoryDtoByStyle(hoodStyleDto);
        BigDecimal totalRentalFee=calculateTotalDeposit(graduationPackageDto);
        BigDecimal totalDeposit=calculateTotalRentalFee(graduationPackageDto);
        BigDecimal totalPrice=totalRentalFee.add(totalDeposit);

        PackageWithStyleAndInventoryDto res=new PackageWithStyleAndInventoryDto(graduationPackageDto.getPackageId(),graduationPackageDto.getEducationLevel(),graduationPackageDto.getInstitution(),graduationPackageDto.getFaculty()
        ,hatStyleWithInventoryDto,gownStyleWithInventoryDto,hoodStyleWithInventoryDto,totalDeposit,totalRentalFee,totalPrice);

        return res;
    }

    //Given date return the style the dates and the available quantity//
    public InventoryDateAndQuantityDto getInventoryAvailableDateAndQuantity(InventoryDto inventoryDto,LocalDate date){
        if(inventoryDto==null){
            return null;
        }
        String modelId=inventoryDto.getModelId();
        InventoryQuantityTrackDto inventoryQuantityTrackDto = inventoryQuantityTrackService.getInventoryQuantityTrackByDate(modelId, date);
        int total=inventoryDto.getTotalQty();
        int availableQty=total;
        List<ItemHoldDto> itemHoldDtos= itemHoldService.getActiveItemHoldForDate(modelId, date);
        int on_hold_qty=0;
        for(ItemHoldDto itemHoldDto : itemHoldDtos){
            on_hold_qty+=itemHoldDto.getQty();

        }
        int damageQty= damageLogService.getDamagedQty(modelId, date);
        
        if(inventoryQuantityTrackDto!=null){
            int unavailableQty=inventoryQuantityTrackDto.getBackupQty()+inventoryQuantityTrackDto.getRentedQty()+inventoryQuantityTrackDto.getReservedQty()+inventoryQuantityTrackDto.getWashQty()+on_hold_qty+damageQty;
            availableQty=availableQty-unavailableQty;

            
            
        }
        else{
            availableQty=availableQty-on_hold_qty-10;
        }
        return new InventoryDateAndQuantityDto(inventoryDto,date,availableQty);

    }

    public DailyAvailabilityDto getDayAvailability(String hatModelId,String hoodModelId,String gownModelId,LocalDate date)throws RuntimeException,ModelNotFoundException{
        List<ComponentAvailabilityDto> componentAvailabilityDtos=new ArrayList<>();
        
        if(hatModelId!=null){
            InventoryDto hatModelDto=inventoryService.getByModelId(hatModelId);
            InventoryDateAndQuantityDto hatModelAvailable=getInventoryAvailableDateAndQuantity(hatModelDto, date);
            int min=hatModelAvailable.getAvailableQty();
            for(int j=0;j<7;j++){
                LocalDate prempt=date.plusDays(j);
                hatModelAvailable=getInventoryAvailableDateAndQuantity(hatModelDto, prempt);
                if(hatModelAvailable.getAvailableQty()<min){
                    min=hatModelAvailable.getAvailableQty();
                }
            }
            componentAvailabilityDtos.add(new ComponentAvailabilityDto(hatModelDto,min));

        }
        if(hoodModelId!=null){
            InventoryDto hoodModelDto=inventoryService.getByModelId(hoodModelId);
            InventoryDateAndQuantityDto hoodModelAvailable=getInventoryAvailableDateAndQuantity(hoodModelDto,date);
            int min=hoodModelAvailable.getAvailableQty();
            for(int j=0;j<7 ;j++){
                LocalDate prempt=date.plusDays(j);
                hoodModelAvailable=getInventoryAvailableDateAndQuantity(hoodModelDto, prempt);
                if(hoodModelAvailable.getAvailableQty()<min){
                    min=hoodModelAvailable.getAvailableQty();
                }
            }
            componentAvailabilityDtos.add(new ComponentAvailabilityDto(hoodModelDto,min));
            
            
        }
        if(gownModelId!=null){
            
            
            InventoryDto gownModelDto=inventoryService.getByModelId(gownModelId);
            InventoryDateAndQuantityDto gownModelAvailable=getInventoryAvailableDateAndQuantity(gownModelDto, date);
            int min=gownModelAvailable.getAvailableQty();
            for(int j=0;j<7 ;j++){
                LocalDate prempt=date.plusDays(j);
                gownModelAvailable=getInventoryAvailableDateAndQuantity(gownModelDto, prempt);
                if(gownModelAvailable.getAvailableQty()<min){
                    min=gownModelAvailable.getAvailableQty();
                }
            }
            componentAvailabilityDtos.add(new ComponentAvailabilityDto(gownModelDto,min));
            
        }
        if(componentAvailabilityDtos.size()==0){
            throw new RuntimeException("No Ids chosen.");
        }
        
        int minAvailableQty=Integer.MAX_VALUE;
        for (ComponentAvailabilityDto componentAvailabilityDto:componentAvailabilityDtos){
            if (componentAvailabilityDto.getAvailableQty()<minAvailableQty){
                minAvailableQty=componentAvailabilityDto.getAvailableQty();
            }

        }


        return new DailyAvailabilityDto(date,componentAvailabilityDtos,minAvailableQty);

            
            

    }

    //Given 3 modelId and date , return all date and quantity of this set for the next 90 days;
    public List<DailyAvailabilityDto> getAvailableQtyForSet (String hatModelId,String hoodModelId,String gownModelId) throws RuntimeException,ModelNotFoundException{
        List<DailyAvailabilityDto> res= new ArrayList<>();
        LocalDate today=LocalDate.now();
        for(int i=0;i<7;i++){
            LocalDate curr=today.plusDays(i);
            List<ComponentAvailabilityDto> componentAvailabilityDtos=new ArrayList<>();
            if(hatModelId!=null){
                InventoryDto hatModelDto=inventoryService.getByModelId(hatModelId);
                InventoryDateAndQuantityDto hatModelAvailable=getInventoryAvailableDateAndQuantity(hatModelDto, curr);
                int min=hatModelAvailable.getAvailableQty();
                for(int j=0;j<7 && i+j<90;j++){
                    LocalDate prempt=curr.plusDays(j);
                    hatModelAvailable=getInventoryAvailableDateAndQuantity(hatModelDto, prempt);
                    if(hatModelAvailable.getAvailableQty()<min){
                        min=hatModelAvailable.getAvailableQty();
                    }
                }
                componentAvailabilityDtos.add(new ComponentAvailabilityDto(hatModelDto,min));

            }
            if(hoodModelId!=null){
                InventoryDto hoodModelDto=inventoryService.getByModelId(hoodModelId);
                InventoryDateAndQuantityDto hoodModelAvailable=getInventoryAvailableDateAndQuantity(hoodModelDto, curr);
                int min=hoodModelAvailable.getAvailableQty();
                for(int j=0;j<7 && i+j<90;j++){
                    LocalDate prempt=curr.plusDays(j);
                    hoodModelAvailable=getInventoryAvailableDateAndQuantity(hoodModelDto, prempt);
                    if(hoodModelAvailable.getAvailableQty()<min){
                        min=hoodModelAvailable.getAvailableQty();
                    }
                }
                componentAvailabilityDtos.add(new ComponentAvailabilityDto(hoodModelDto,min));
                
                
            }
            if(gownModelId!=null){
                
                
                InventoryDto gownModelDto=inventoryService.getByModelId(gownModelId);
                InventoryDateAndQuantityDto gownModelAvailable=getInventoryAvailableDateAndQuantity(gownModelDto, curr);
                int min=gownModelAvailable.getAvailableQty();
                for(int j=0;j<7 && i+j<90;j++){
                    LocalDate prempt=curr.plusDays(j);
                    gownModelAvailable=getInventoryAvailableDateAndQuantity(gownModelDto, prempt);
                    if(gownModelAvailable.getAvailableQty()<min){
                        min=gownModelAvailable.getAvailableQty();
                    }
                }
                componentAvailabilityDtos.add(new ComponentAvailabilityDto(gownModelDto,min));
                
            }
            if(componentAvailabilityDtos.size()>0){
                int minAvailableQty=Integer.MAX_VALUE;
                for (ComponentAvailabilityDto componentAvailabilityDto:componentAvailabilityDtos){
                    if (componentAvailabilityDto.getAvailableQty()<minAvailableQty){
                        minAvailableQty=componentAvailabilityDto.getAvailableQty();
                    }

                }
                res.add(new DailyAvailabilityDto(curr,componentAvailabilityDtos,minAvailableQty));

            }
            
            
            
            


        }
        if(res.size()==0){
            throw new RuntimeException("No Items Selected.");
        }

        return res;
    }

    


    


    
}
