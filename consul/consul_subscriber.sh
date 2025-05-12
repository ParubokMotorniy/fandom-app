#!/bin/bash/

set -x

for file in /registration/3rdparty_services/* ; do
    echo "[+] Subscribing ${file}"
    curl -X PUT --data @$file http://${CONSUL_HOST}:${CONSUL_PORT}/v1/agent/service/register -v
done

