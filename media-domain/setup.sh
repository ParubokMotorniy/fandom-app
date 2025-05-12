#!/bin/sh

GLUSTER_VOLUME="gv0"
MOUNT_PATH="/mnt/glusterfs-root"

mkdir -p "$MOUNT_PATH"

# Wait for volume to be listed
while [ "$(gluster volume list | grep -w "$GLUSTER_VOLUME")" = "" ]; do
    echo "Waiting for volume to get created"
    sleep 2
done

# Wait for volume to be started
while ! gluster volume info "$GLUSTER_VOLUME" | grep -q "Status: Started"; do
    echo "Waiting for volume to get started"
    sleep 2
done

# Mount and setup
mount -t glusterfs localhost:/$GLUSTER_VOLUME "$MOUNT_PATH"
mkdir -p "$MOUNT_PATH/media"

echo "Configuring Apache to serve media..."

a2enmod rewrite headers
a2dissite 000-default default-ssl
a2ensite fandomapp.uwu

echo "Restarting Apache..."
service apache2 restart

exec apachectl -D FOREGROUND
