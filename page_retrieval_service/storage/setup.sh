#!/bin/bash

GLUSTER_VOLUME="gv0"
MOUNT_PATH="/mnt/glusterfs-root"

# Create mount point
mkdir -p "$MOUNT_PATH"

# Wait for volume to be created
while ! [ "$(/usr/sbin/gluster volume list)" = "${GLUSTER_VOLUME}" ]; do
    echo "Waiting for volume to get created"
    sleep 5
done

# Wait for volume to start
while [ "$(/usr/sbin/gluster volume info | grep Status | cut -d' ' -f2)" != "Started" ]; do
    echo "Waiting for volume to get started"
    sleep 5
done

# Mount GlusterFS volume
mount -t glusterfs localhost:/$GLUSTER_VOLUME "$MOUNT_PATH"
mkdir -p ${MOUNT_PATH}/media

echo "Configuring Apache to serve media..."

# Configure Apache
a2enmod rewrite headers
a2dissite 000-default default-ssl
a2ensite fandomapp.uwu

echo "Restarting Apache..."
service apache2 restart

# Start Apache in foreground
exec apachectl -D FOREGROUND