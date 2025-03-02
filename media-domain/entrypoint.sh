#!/bin/sh

# Start GlusterFS daemon
glusterd --no-daemon &

# Wait for glusterd to start
sleep 5

# Ensure the data directory exists
mkdir -p /data

other_hosts="${@}"

for host in ${other_hosts};do
    echo "Pinging host ${host}"
    until gluster peer probe ${host} &> /dev/null; do
        echo "Waiting for host ${host}..."
        sleep 2
    done
done

sleep 5
