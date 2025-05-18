#!/bin/bash/

set -x

while ! ping ${CONSUL_HOST} -c 3; do
    echo "[-] Consul unavailable!"
    sleep 1
done

echo "[+] Consul available!"

for file in /registration/3rdparty_services/* ; do
    echo "[+] Subscribing ${file}"
    curl -X PUT --data @$file http://${CONSUL_HOST}:${CONSUL_PORT}/v1/agent/service/register -v
done

for file in /configuration/configs/* ; do
    echo "[+] Putting a key-value item ${file} into consul"
    FILENAME=$(echo "${file}" | cut -d'/' -f4)
    curl -X PUT --data @$file http://${CONSUL_HOST}:${CONSUL_PORT}/v1/kv/$FILENAME -v
done

