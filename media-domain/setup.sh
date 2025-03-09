#!/bin/sh

GLUSTER_VOLUME="gv0"
MOUNT_PATH="/mnt/glusterfs-root"

mkdir -p "$MOUNT_PATH"

set -x

while ! [ $(gluster volume list) = ${GLUSTER_VOLUME} ];do
    sleep 1
done

mount -t glusterfs localhost:/$GLUSTER_VOLUME "$MOUNT_PATH"

echo "Configuring Apache to serve media..."

APACHE_CONF="/etc/apache2/sites-available/000-default.conf"

cat <<EOF > "$APACHE_CONF"
<VirtualHost *:80>
    DocumentRoot $MOUNT_PATH
    <Directory $MOUNT_PATH>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
    ErrorLog \${APACHE_LOG_DIR}/error.log
    CustomLog \${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOF

# Enable Apache modules (optional)
a2enmod rewrite headers

echo "Starting Apache..."
service apache2 restart
exec apachectl -D FOREGROUND