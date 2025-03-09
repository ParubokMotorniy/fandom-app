#!/bin/sh

glusterd --no-daemon &

sleep 5

# Ensure the data directory exists
mkdir -p /data/brick

total_hosts=3
other_hosts="${@}"

while [ $( gluster pool list | wc -l ) -lt $((total_hosts + 1)) ];do
    for host in ${other_hosts};do
        echo "Pinging host ${host}"
        gluster peer probe ${host}
    done
done

sleep 5
