#!/bin/sh

GLUSTER_VOLUME="gv0"
MOUNT_PATH="/mnt/glusterfs-root"

mkdir -p "$MOUNT_PATH"

while ! [ $(gluster volume list) = ${GLUSTER_VOLUME} ];do
    echo "Waiting for volume to get created"
done

while [ $(gluster volume info | grep Status | cut -d' ' -f2) != "Started" ];do
    echo "Waiting for voulme to get started"
done

mount -t glusterfs localhost:/$GLUSTER_VOLUME "$MOUNT_PATH"
mkdir ${MOUNT_PATH}/media

echo "Configuring Apache to serve media..."

a2enmod rewrite headers
a2dissite 000-default default-ssl
a2ensite fandomapp.uwu

echo "Restarting Apache..."
service apache2 restart

exec apachectl -D FOREGROUND
