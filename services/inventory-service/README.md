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


### 1. Getting availability of Hood,Gown,Hat on any given date

In Postman, using get

http://localhost:8080/api/inventory/availability?hatModelId=0000024&hoodModelId=0000002&gownModelId=0100020&date=2026-03-15

this will return available qty of the whole set, the available qty of each component as well

### 3. Getting availability of Hood, Gown, Hat for the next 90 days

In Postman, using get

http://localhost:8080/api/inventory/availability90?hatModelId=0000024&hoodModelId=0000002&gownModelId=0100020

this will return available qty of the whole set, the available qty of each component as well for the next 90 days starting from the date this was requested.

### 4. Get all packages and its pricing, including style , faculty etc.

http://localhost:8080/api/inventory/packages/all

### 5. Get package and its pricing, including style,  faculty , filtering based on the institution, educationLevel and faculty


http://localhost:8080/api/inventory/packages?institution=NUS

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

http://localhost:8080/api/inventory/reserveItems

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

http://localhost:8080/api/inventory/collectItems

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

http://localhost:8080/api/inventory/washItems

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




