#!/bin/sh

export CONSUL_HOST="192.168.56.2"
export CONSUL_PORT="8500"

curl -X PUT --data @configs/rabbitmq-config http://"$CONSUL_HOST":"$CONSUL_PORT"/v1/kv/rabbitmq-config
curl -X PUT --data @services/elastic.json http://"$CONSUL_HOST":"$CONSUL_PORT"/v1/agent/service/register

