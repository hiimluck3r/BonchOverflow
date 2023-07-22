# BonchOverflow

> "Это как стаковерфлоу, только хуже!" (с) Анонимный пользователь

Однажды вечером я задался вопросом: *"Почему наши студенты задают вопросы через какую-то стороннюю группу, ожидая долгой модерации, да еще и в VK?"*. 

Такой расклад меня не устроил, поэтому в течение 1 дня и 2 ночей был написан BonchOverflow - бот с системой вопрос-ответ внутри Telegram (PostgreSQL powered).

**docker-compose.yml:**

```bazaar
version: '3.9'
services:
  db:
    container_name: pg_container
    image: postgres:15
    restart: always
    environment:
      POSTGRES_USER: dbusername
      POSTGRES_PASSWORD: dbpassword
      POSTGRES_DB: bonchoverflow_db
    ports:
      - "5432:5432"
    volumes:
      - ./postgresql:/docker-entrypoint-initdb.d
      - ./postgresql/data:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin4_container
    image: dpage/pgadmin4
    restart: always
    environment:
      PGADMIN_DEFAULT_EMAIL: example@example.com
      PGADMIN_DEFAULT_PASSWORD: yourpasswordhere
    ports:
      - "80:80"

  bonchoverflow:
    container_name: bonchoverflow_bot
    image: luck3rinc/bonchoverflow
    restart: on-failure
    environment:
      API_TOKEN: yourtokenhere
      HOST: db
      DB: bonchoverflow_db
      USER: dbusername
      PWD: dbpassword
      ADMIN: yourtelegramid
    volumes:
      - ./logs:/~/BonchOverflow/logs
    depends_on:
      - db

  bonchoverflow_support:
    container_name: bonchoverflow_supportbot
    image: luck3rinc/bonchoverflow_support
    restart: on-failure
    environment:
      SUPPORT_TOKEN: yourtokenhere
      ADMIN: yourtelegramid

volumes:
  logs:
```

Опробовать бота можно в Telegram: *@bonchoverflow_bot*

**Пожалуйста, не оффтопьте там :)**