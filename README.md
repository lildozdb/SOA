# SOA

# C4Container
    title Container diagram for Marketplace System

    Person(customer, "Покупатель", "Просматривает товары, делает заказы")
    Person(seller, "Продавец", "Управляет своими товарами")

    System_Boundary(c1, "Marketplace") {
        Container(web_app, "API Gateway", "Nginx/Go", "Входная точка, проверка токенов")
        
        Container(user_svc, "User Service", "Python/FastAPI", "Управление пользователями и ролями", "PostgreSQL")
        Container(catalog_svc, "Catalog Service", "Python/FastAPI", "Каталог товаров и остатки", "MongoDB/PostgreSQL")
        Container(order_svc, "Order Service", "Python/FastAPI", "Управление заказами и корзиной", "PostgreSQL")
        Container(payment_svc, "Payment Service", "Python/FastAPI", "Обработка платежей")
        
        ContainerDb(message_bus, "Message Broker", "RabbitMQ/Kafka", "Асинхронная связь (события)")
        
        Container(notif_svc, "Notification Service", "Python/FastAPI", "Email/Push уведомления")
        Container(rec_svc, "Recommendation Service", "Python/FastAPI", "Персональная лента (ML)")
    }

    System_Ext(bank, "Payment Gateway", "Внешний банк")

    Rel(customer, web_app, "Использует", "HTTPS/JSON")
    Rel(seller, web_app, "Использует", "HTTPS/JSON")
    
    Rel(web_app, user_svc, "Запросы профиля", "REST")
    Rel(web_app, catalog_svc, "Просмотр товаров", "REST")
    Rel(web_app, order_svc, "Создание заказа", "REST")

    Rel(order_svc, payment_svc, "Вызов оплаты", "Sync REST")
    Rel(payment_svc, bank, "Проведение транзакции")

    Rel(order_svc, message_bus, "Событие 'Заказ создан'")
    Rel(message_bus, notif_svc, "Отправка уведомления")
    Rel(message_bus, rec_svc, "Аналитика покупок")
