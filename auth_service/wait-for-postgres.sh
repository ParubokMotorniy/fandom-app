#!/bin/bash
set -e

# Hard-coded values as a fallback (will be overridden by parameters if provided)
DB_HOST=${1:-"postgres-auth"}
DB_USER=${2:-"postgres"}
#hardcoded password for testing, without any security
DB_PASSWORD=${3:-"password"}

DB_NAME=${4:-"auth_db"}
DB_PORT=${5:-"5432"}
#Set
# If there are additional parameters (the command to run), shift them into position
if [ "$#" -gt 5 ]; then
    shift 5
    CMD="$@"
elif [ "$#" -gt 1 ]; then
    # If we have at least 2 parameters, assume the last ones are the command
    # This handles the case where some but not all DB parameters were passed
    shift
    CMD="$@"
else
    # Default command if none provided
    CMD="echo 'No command specified, exiting' && exit 0"
fi

echo "============== CONNECTION DETAILS 5=============="
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "User: $DB_USER"
echo "Database: $DB_NAME"
echo "Password length: ${#DB_PASSWORD} characters"
echo "Password: $DB_PASSWORD"
echo "Command to execute: $CMD"
echo "=============================================="

echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
count=0

until PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  count=$((count + 1))
  >&2 echo "Attempt $count: Postgres is unavailable - sleeping"
  >&2 echo "Command: PGPASSWORD=*** psql -h $DB_HOST -U $DB_USER -p $DB_PORT -d $DB_NAME"
  
  # Every 5 attempts, try to ping the host to verify network connectivity
  if [[ $((count % 5)) -eq 0 ]]; then
    >&2 echo "Testing network connectivity to $DB_HOST..."
    ping -c 1 $DB_HOST >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      >&2 echo "Network connectivity OK: Can ping $DB_HOST"
    else
      >&2 echo "Network connectivity FAILED: Cannot ping $DB_HOST"
    fi
    
    # Try to connect to the port with a simple TCP connection
    >&2 echo "Testing TCP connection to $DB_HOST:$DB_PORT..."
    timeout 3 bash -c "cat < /dev/null > /dev/tcp/$DB_HOST/$DB_PORT" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      >&2 echo "TCP connection OK: Port $DB_PORT is open on $DB_HOST"
    else
      >&2 echo "TCP connection FAILED: Cannot connect to $DB_HOST:$DB_PORT"
    fi
  fi
  
  sleep 1
done

>&2 echo "Postgres is up - executing command: $CMD"
exec $CMD