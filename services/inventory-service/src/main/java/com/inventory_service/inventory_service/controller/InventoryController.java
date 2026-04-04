package com.inventory_service.inventory_service.controller;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.ResponseEntity;

import com.inventory_service.inventory_service.dto.DailyAvailabilityDto;
import com.inventory_service.inventory_service.dto.DamageAndQtyDto;
import com.inventory_service.inventory_service.dto.ItemAndDamageIdDto;
import com.inventory_service.inventory_service.dto.ModelIdAndQtyAndDateDto;
import com.inventory_service.inventory_service.dto.PackageWithPriceDto;
import com.inventory_service.inventory_service.dto.PackageWithStyleAndInventoryDto;
import com.inventory_service.inventory_service.dto.ReserveDto;
import com.inventory_service.inventory_service.dto.SoftHoldDto;
import com.inventory_service.inventory_service.dto.StockOverviewRowDto;
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

    // Scenario contract alias: GET /inventory/catalogue
    @GetMapping("/catalogue")
    public InventoryResponse<List<PackageWithPriceDto>> getCatalogue(
        @RequestParam(required = false) String institution,
        @RequestParam(required = false) String educationLevel,
        @RequestParam(required = false) String faculty
    ){
        if (institution == null && educationLevel == null && faculty == null) {
            return new InventoryResponse<List<PackageWithPriceDto>>(200, "success", getService.getAllPackagesWithPricing());
        }
        return new InventoryResponse<List<PackageWithPriceDto>>(200, "success", getService.getAllPackagesMatched(educationLevel, faculty, institution));
    }

    @GetMapping("/stock-overview")
    public InventoryResponse<List<StockOverviewRowDto>> getStockOverview(
        @RequestParam(required = false) LocalDate date
    ){
        LocalDate targetDate = date != null ? date : LocalDate.now();
        return new InventoryResponse<List<StockOverviewRowDto>>(
            200,
            "success",
            getService.getStockOverview(targetDate)
        );
    }

    @GetMapping("/{packageId}")
    public InventoryResponse<PackageWithStyleAndInventoryDto> getPackageWithStyleAndInventory(@PathVariable int packageId){
        InventoryResponse<PackageWithStyleAndInventoryDto> res;
        try {
            PackageWithStyleAndInventoryDto packageWithStyleAndInventoryDto = getService.getPackageWithStyleAndInventory(packageId);
            res= new InventoryResponse<PackageWithStyleAndInventoryDto>(200, "success", packageWithStyleAndInventoryDto);
        } catch (PackageNotFoundException e) {
            res= new InventoryResponse<PackageWithStyleAndInventoryDto>(400, e.getMessage(), null);
        }
        return res;
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

    // Scenario contract alias: POST /inventory/soft-hold
    @PostMapping("/soft-hold")
    public InventoryResponse<SoftHoldDto> softHoldAlias(@RequestBody List<ModelIdAndQtyAndDateDto>items){
        return softHold(items);
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

    // Scenario contract: PUT /inventory/stock/transition
    // Supported transitions:
    // - AVAILABLE_TO_RESERVED (requires holdId + items)
    // - RESERVED_TO_RENTED (requires items)
    // - RENTED_TO_WASH (requires items)
    @PutMapping("/stock/transition")
    public ResponseEntity<InventoryResponse<String>> transitionStock(@RequestBody Map<String, Object> payload){
        try {
            String transition = String.valueOf(payload.getOrDefault("transition", ""));
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> rawItems = (List<Map<String, Object>>) payload.get("items");
            List<ModelIdAndQtyAndDateDto> items = rawItems == null
                ? List.of()
                : rawItems.stream().map(item -> {
                    ModelIdAndQtyAndDateDto dto = new ModelIdAndQtyAndDateDto();
                    dto.setModelId(String.valueOf(item.get("modelId")));
                    dto.setQty(Integer.parseInt(String.valueOf(item.getOrDefault("qty", 1))));
                    dto.setChosenDate(LocalDate.parse(String.valueOf(item.get("chosenDate"))));
                    return dto;
                }).toList();

            switch (transition) {
                case "AVAILABLE_TO_RESERVED":
                    String holdId = String.valueOf(payload.getOrDefault("holdId", ""));
                    postService.reserveItems(new ReserveDto(holdId, items));
                    return ResponseEntity.ok(
                        new InventoryResponse<String>(200, "Success: moved available -> reserved", null)
                    );
                case "RESERVED_TO_RENTED":
                    postService.collectItems(items);
                    return ResponseEntity.ok(
                        new InventoryResponse<String>(200, "Success: moved reserved -> rented", null)
                    );
                case "RENTED_TO_WASH":
                    postService.washItems(items);
                    return ResponseEntity.ok(
                        new InventoryResponse<String>(200, "Success: moved rented -> wash", null)
                    );
                case "REPAIR_TO_WASH":
                    postService.moveRepairToWash(items);
                    return ResponseEntity.ok(
                        new InventoryResponse<String>(200, "Success: moved repair -> wash", null)
                    );
                case "RENTED_TO_DAMAGED":
                    postService.damageItems(items);
                    return ResponseEntity.ok(
                        new InventoryResponse<String>(200, "Success: moved rented -> damaged", null)
                    );
                case "DAMAGED_TO_REPAIR":
                    postService.moveDamagedToRepair(items);
                    return ResponseEntity.ok(
                        new InventoryResponse<String>(200, "Success: moved damaged -> repair", null)
                    );
                case "WASH_TO_AVAILABLE":
                    postService.moveWashToAvailable(items);
                    return ResponseEntity.ok(
                        new InventoryResponse<String>(200, "Success: moved wash -> available", null)
                    );
                default:
                    return ResponseEntity.badRequest().body(
                        new InventoryResponse<String>(400, "Unsupported transition type", null)
                    );
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(
                new InventoryResponse<String>(400, e.getMessage(), null)
            );
        }
    }

    // Scenario contract alias: PUT /inventory/maintenance/request
    @PutMapping("/maintenance/request")
    public ResponseEntity<InventoryResponse<String>> maintenanceRequest(@RequestBody Map<String, Object> payload){
        payload.put("transition", "DAMAGED_TO_REPAIR");
        return transitionStock(payload);
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
