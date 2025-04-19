# fandom-app

Project structure:

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