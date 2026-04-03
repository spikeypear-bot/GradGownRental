# SETTING UP THE SERVICE

Run in the root terminal where the yaml file lies in

`docker compose up --build `

inventory-service-db -> port 1234:5432
inventory-service -> 8080:8080

To view the databases, run in the terminal 

`docker exec -it my-postgres psql -U postgres`

`SET search_path TO inventory_service;`
`select * from inventory limit 5;` 




# TESTING THE SERVICE



The 9 main features that has been set up includes, 


### 1. Finding Package by PackageId

In Postman, using get 

http://localhost:8080/api/inventory/{packageId}

this will return package and its different model id (shows all the size)


### 2. Getting availability of Hood,Gown,Hat on any given date

In Postman, using get

http://localhost:8080/api/inventory/availability?hatModelId=0000024&hoodModelId=0000002&gownModelId=0100020&date=2026-03-15

this will return available qty of the whole set, the available qty of each component as well

### 3. Getting availability of Hood, Gown, Hat for the next 90 days

In Postman, using get

http://localhost:8080/api/inventory/availability90?hatModelId=0000024&hoodModelId=0000002&gownModelId=0100020

this will return available qty of the whole set, the available qty of each component as well for the next 90 days starting from the date this was requested.

### 4. Get all packages and its pricing, including style , faculty etc.

http://localhost:8080/api/inventory/catalogue

### 5. Get package and its pricing, including style,  faculty , filtering based on the institution, educationLevel and faculty


http://localhost:8080/api/inventory/catalogue?institution=NUS

this will return all with NUS as institution

### 6. Soft-Locking ids and its quantity returns a itemHoldID generated using a UUID

POST 

http://localhost:8080/api/inventory/softlock

Body:

[{
    "modelId":"0000024",
    "qty":30,
    "chosenDate":"2026-03-15"
},
{
    "modelId":"0000002",
    "qty":30,
    "chosenDate":"2026-03-15"
},
{
    "modelId":"0100020",
    "qty":30,
    "chosenDate":"2026-03-15"
}]

returns a hold id , and its other relevant details

### 7. Reserving Items once item is bought

POST 

http://localhost:8080/api/inventory/reserveitems

Body: 

{"holdId":"35b7d04a-47ad-4cd7-ab9a-fde986a22ead",
    "items":
    [{
        "modelId":"0000024",
        "qty":30,
        "chosenDate":"2026-03-15"
    },
    {
        "modelId":"0000002",
        "qty":30,
        "chosenDate":"2026-03-15"
    },
    {
        "modelId":"0100020",
        "qty":30,
        "chosenDate":"2026-03-15"
    }]
}

### 8. Collect Items once customer collected Items

PUT

http://localhost:8080/api/inventory/collectitems

[
    
    {
        "modelId":"0000024",
        "qty":30,
        "chosenDate":"2026-03-15"
    },
    {
        "modelId":"0000002",
        "qty":30,
        "chosenDate":"2026-03-15"
    },
    {
        "modelId":"0100020",
        "qty":30,
        "chosenDate":"2026-03-15"
    }
]

### 9. Once Items come back, set these to washing

PUT

http://localhost:8080/api/inventory/washitems

[
    
    {
        "modelId":"0000024",
        "qty":30,
        "chosenDate":"2026-03-15"
    },
    {
        "modelId":"0000002",
        "qty":30,
        "chosenDate":"2026-03-15"
    },
    {
        "modelId":"0100020",
        "qty":30,
        "chosenDate":"2026-03-15"
    }
]

### More features like returning of damaged, or returning of washed clothes , as there is more to be discussed. 


# Structures of the service

Entities -> Repository -> Service -> Controller (Entrypoint for API)

Entities: GraduationPackage, Inventory , Inventory Style, ItemHold 

Repository: ^^

Service: ^^ + PostService + GetService

Controller: InventoryController

### More features like exceptions and response or request bodies to be added.



## Entities
### 1. InventoryStyle
Refers to the different styles, example like Blue Gown, or Crimson Edge Hood, these two would be different style. All styles have same rental fee and deposit and is defined in this entity. 

### 2. Inventory
Entity keeping track of the total quantities per model, as well as the size of it. 
Two sets of clothings are considered different model, if they have different styles (Mapped by style id), and different sizes
Example: M Blue Gown and S Blue gown is different model, but two of the S blue gown are considered the same model id.

### 3. InventoryQuantityTrack
Tracks quantity of inventory on a day to day basis, whenever an item is first rented on a certain day, a new entry is created mapping the model id to the dates
And to the quantity affected by it. 
Quantities comes in the form of reserved, rented, wash, damaged, backup. Backup is usually kept at 10, and is activated when there happens to be insufficient amount, but order has been made.
When a gown is reserved it would be blocked for 7 days, 3 days being rented and 4 days being sent for washing. 

### 4. GraduationPackage
The Grad package mainly defines the type of packages offered, in particular the different packages maps to different faculty, institution and education level.
Students are only allow to buy packages. 

### 5. ItemHold
Is used for soft holding of items. Tracked by the HoldID as well as modelID and will only be available for 10mins. 

## Repositories

It defines function to allow the service classes to make uses of the entity, defines function to make queries on the tables of the database. 

## Service

Main crux of business logic. Consists of services for each entity, as well as a post service and a get service.

## Controller 
Post mapping and get mapping to connect and receive api calls

## 







