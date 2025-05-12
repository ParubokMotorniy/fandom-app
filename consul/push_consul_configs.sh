#!/bin/sh

export CONSUL_HOST="127.0.0.1"
export CONSUL_PORT="8500"

curl -X PUT --data @configs/kafka_config.cfg http://"$CONSUL_HOST":"$CONSUL_PORT"/v1/kv/kafka-config
curl -X PUT --data @services/elastic.json http://localhost:8500/v1/agent/service/register 

