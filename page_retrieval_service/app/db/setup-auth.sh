#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
until pg_isready -U myuser -d mydb; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 1
done

# Update pg_hba.conf
cat > /var/lib/postgresql/data/pg_hba.conf << EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
host    all             all             0.0.0.0/0               trust
EOF

# Reload PostgreSQL configuration
psql -U myuser -d mydb -c "SELECT pg_reload_conf();" 