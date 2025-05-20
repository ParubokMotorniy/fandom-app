#!/bin/bash

# Start GlusterFS daemon

/usr/sbin/glusterd --no-daemon &

# Wait for daemon to start
sleep 5

# Create brick directory
mkdir -p /data/brick

total_hosts=3
other_hosts="${@}"

# Wait for peers to be available
while [ $(/usr/sbin/gluster pool list | wc -l) -lt $((total_hosts + 1)) ]; do
    for host in ${other_hosts}; do
        echo "Pinging host ${host}"
        /usr/sbin/gluster peer probe ${host}
        sleep 2
    done
    sleep 5
done

# Wait for peer connections to stabilize
sleep 5