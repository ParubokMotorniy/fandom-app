#!/bin/sh

CONSUL_PORT="8500" CONSUL_HOST="127.0.0.1" ELASTIC_PASSWORD="d2PUuG3-UpC-HBfblAWG" ELASTIC_USER="elastic" INSTANCE_HOST=localhost INSTANCE_PORT=7000 fastapi dev --port 7000 ./search_service/search_service.py 
