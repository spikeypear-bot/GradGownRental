package com.inventory_service.inventory_service.controller;

import java.time.LocalDate;
import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.inventory_service.inventory_service.dto.DailyAvailabilityDto;
import com.inventory_service.inventory_service.dto.DamageAndQtyDto;
import com.inventory_service.inventory_service.dto.ItemAndDamageIdDto;
import com.inventory_service.inventory_service.dto.ModelIdAndQtyAndDateDto;
import com.inventory_service.inventory_service.dto.PackageWithPriceDto;
import com.inventory_service.inventory_service.dto.PackageWithStyleAndInventoryDto;
import com.inventory_service.inventory_service.dto.ReserveDto;
import com.inventory_service.inventory_service.dto.SoftHoldDto;
import com.inventory_service.inventory_service.exception.DamageNotFoundException;
import com.inventory_service.inventory_service.exception.ModelNotFoundException;
import com.inventory_service.inventory_service.exception.PackageNotFoundException;
import com.inventory_service.inventory_service.response.InventoryResponse;
import com.inventory_service.inventory_service.service.GetService;
import com.inventory_service.inventory_service.service.PostService;

@RestController
@RequestMapping("/api/inventory")
public class InventoryController {
    private final GetService getService;
    private final PostService postService;

    public InventoryController(GetService getService,PostService postService) {
        this.getService = getService;
        this.postService=postService;
    }

    @GetMapping("/{packageId}")
    public InventoryResponse<PackageWithStyleAndInventoryDto> getPackageWithStyleAndInventory(@PathVariable int packageId){
        InventoryResponse<PackageWithStyleAndInventoryDto> res;
        try {
            PackageWithStyleAndInventoryDto packageWithStyleAndInventoryDto = getService.getPackageWithStyleAndInventory(packageId);
            res= new InventoryResponse<PackageWithStyleAndInventoryDto>(200, "success", packageWithStyleAndInventoryDto);
        } catch (PackageNotFoundException e) {
            res= new InventoryResponse<PackageWithStyleAndInventoryDto>(400, e.getMessage(), null);
            // TODO: handle exception
        }
        return res;
        
        
    }
    @GetMapping("/availability")
    public InventoryResponse<DailyAvailabilityDto> getSetAvailabilityForTheDate(
        @RequestParam(required = false) String hatModelId, 
        @RequestParam(required = false)  String hoodModelId, 
        @RequestParam(required = false)  String gownModelId,
        @RequestParam LocalDate date){
            try {
                return new InventoryResponse<DailyAvailabilityDto>(200, "success", getService.getDayAvailability(hatModelId, hoodModelId, gownModelId, date));
            } catch (RuntimeException e) {
                // TODO: handle exception
                return new InventoryResponse<DailyAvailabilityDto>(0, e.getMessage(), null);
            }
        

    }

    @GetMapping("/availability90")
    public InventoryResponse<List<DailyAvailabilityDto>> getSetAvailabilityWithDate(
        @RequestParam(required = false) String hatModelId, 
        @RequestParam(required = false)  String hoodModelId, 
        @RequestParam(required = false)  String gownModelId){
            try{
                return new InventoryResponse<List<DailyAvailabilityDto>>(200, "success", getService.getAvailableQtyForSet(hatModelId, hoodModelId, gownModelId));
            }
            catch(RuntimeException e){
                return new InventoryResponse<List<DailyAvailabilityDto>>(400, e.getMessage(), null);


            }
            


    }

    @GetMapping("/packages/all")
    public InventoryResponse<List<PackageWithPriceDto>> getAllPackages(){
        return new InventoryResponse<List<PackageWithPriceDto>>(200, "success", getService.getAllPackagesWithPricing());

    }

    @GetMapping("/packages")
    public InventoryResponse<List<PackageWithPriceDto>> getFilteredPackages(
        @RequestParam(required = false) String institution,
        @RequestParam(required = false) String educationLevel,
        @RequestParam(required=false) String faculty
    ){
        return new InventoryResponse<List<PackageWithPriceDto>>(200, "success", getService.getAllPackagesMatched(educationLevel, faculty, institution));
    }
    

    @PostMapping("/softlock")
    public InventoryResponse<SoftHoldDto> softHold(@RequestBody List<ModelIdAndQtyAndDateDto>items){

        try {
            return new InventoryResponse<SoftHoldDto>(200, "success", postService.makeSoftHold(items));
            
            
        } catch (RuntimeException e) {
            return new InventoryResponse<SoftHoldDto>(400, e.getMessage(), null);

            // TODO: handle exception
        }

    }

    @PostMapping("/reserveitems")
    public InventoryResponse<String> reserveItemsInventory(@RequestBody ReserveDto items){
        try {
            postService.reserveItems(items);
            return new InventoryResponse<String>(200, "Success: Items reserved successfully", null);
            
            
        }
        
        catch (RuntimeException e) {
            return new InventoryResponse<String>(400, e.getMessage(), null);

            // TODO: handle exception
        }

    }

    @PutMapping("/collectitems")
    public InventoryResponse<String> collectItemsUpdate(@RequestBody List<ModelIdAndQtyAndDateDto> items){
        try {
            postService.collectItems(items);
            return new InventoryResponse<String>(200, "Success: Items collected by customers", null);
            
            
        } catch (ModelNotFoundException e) {
            return new InventoryResponse<String>(400, e.getMessage(), null);

            // TODO: handle exception
        }

    }

    @PutMapping ("/washitems")
    public InventoryResponse<String> putItemsUpdate(@RequestBody List<ModelIdAndQtyAndDateDto> items){
        try {
            postService.washItems(items);
            return new InventoryResponse<String>(200, "Success: Items collected from customer and sent for washing", null);
            
            
        } catch (ModelNotFoundException e) {
            return new InventoryResponse<String>(400, e.getMessage(), null);

            // TODO: handle exception
        }
    }

    @PostMapping("/damageitems")
    public InventoryResponse<List<ItemAndDamageIdDto>> createDamageItems(@RequestBody List<ModelIdAndQtyAndDateDto> items){
        try {
            List<ItemAndDamageIdDto> res=postService.damageItems(items);
            return new InventoryResponse<List<ItemAndDamageIdDto>>(200, "Success: Damage Items Logged",res );
            
            
        } catch (RuntimeException e) {

            return new InventoryResponse<List<ItemAndDamageIdDto>>(400, e.getMessage(), null);

            // TODO: handle exception
        }
    }

    @PostMapping("/repairitems")
    public InventoryResponse<List<Integer>> createRepairItems(@RequestBody List<DamageAndQtyDto>repairList){
        try {
            postService.repairItems(repairList);
            return new InventoryResponse<List<Integer>>(200, "Success: Damage Logs Updated", null);
        } catch (DamageNotFoundException e) {
            return new InventoryResponse<List<Integer>>(400, "Error: Damage Id for the following cannot be found", e.getErrors());
            
        }

    }

    
    
    

    
}
