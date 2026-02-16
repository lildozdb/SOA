# C4
flowchart TD
    %% Линии и связи
    Customer((Покупатель))
    Seller((Продавец))

    subgraph Marketplace_System [Система Маркетплейса]
        Gateway[API Gateway<br/><i>Nginx/Go</i>]
        
        subgraph Services [Микросервисы]
            UserSvc[User Service<br/><b>Python/FastAPI</b>]
            CatalogSvc[Catalog Service<br/><b>Python/FastAPI</b>]
            OrderSvc[Order Service<br/><b>Python/FastAPI</b>]
            PaymentSvc[Payment Service<br/><b>Python/FastAPI</b>]
            NotifSvc[Notification Service<br/><b>Python/FastAPI</b>]
            RecSvc[Recommendation Service<br/><b>Python/FastAPI</b>]
        end

        Broker[(Message Broker<br/>RabbitMQ)]
        
        DB1[(User DB<br/>PostgreSQL)]
        DB2[(Catalog DB<br/>PostgreSQL)]
        DB3[(Order DB<br/>PostgreSQL)]
    end

    ExternalBank[Payment Gateway<br/><i>External API</i>]

    %% Взаимодействия
    Customer --> Gateway
    Seller --> Gateway
    
    Gateway --> UserSvc
    Gateway --> CatalogSvc
    Gateway --> OrderSvc

    UserSvc -.-> DB1
    CatalogSvc -.-> DB2
    OrderSvc -.-> DB3

    OrderSvc -- "Sync REST" --> PaymentSvc
    PaymentSvc --> ExternalBank

    OrderSvc -- "Events" --> Broker
    Broker --> NotifSvc
    Broker --> RecSvc
