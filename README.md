# fandom-app

## Services

| Service | Ports | Method | Endpoint | Description |
|---|---|---|---|---|
| Page Retrieval Service | 8001, 8003, 8004  | GET  | `/api/page/{page_id}`      | Retrieves the content of a specific page based on its ID. |
|                        |                   | POST | `/api/internal/store-page` | idk |
|                        |                   | GET  | `/api/pages/`              | Returns a list of all available pages. |
| Page Adding Service    | 8002              | POST | `/api/add-page`            | Adds a new page to the DB. |


Project structure:
```
/
│
├── api_gateway/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── middleware/
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
│
├── auth_service/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
│
├── page_retrieval_service/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── db/
│   │   └── media/
│   ├── requirements.txt
│   └── Dockerfile
│
├── page_adding_service/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   └── services/
│   ├── requirements.txt
│   └── Dockerfile
│
├── page_search_service/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   └── elastic/
│   ├── requirements.txt
│   └── Dockerfile
│
├── page_message_queue/
│   ├── producer.py
│   ├── consumer.py
│   ├── kafka_config.py
│   └── requirements.txt
│
├── shared_libs/
│   ├── config/
│   ├── auth_utils/
│   └── schemas/
│
├── docker-compose.yml
├── .env
└── README.md
```
