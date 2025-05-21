FROM python:3.9

WORKDIR /app

# Install PostgreSQL client for the wait script
RUN apt-get update && apt-get install -y postgresql-client

# Configure psql to use TCP by default
RUN mkdir -p ~/.postgresql && echo "host=postgres" > ~/.postgresql/pgpass

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add the wait script and make it executable
COPY wait-for-postgres.sh /wait-for-postgres.sh
RUN chmod +x /wait-for-postgres.sh

# Set PGHOST environment variable to force TCP connections
ENV PGHOST=postgres

# Default command
CMD ["/wait-for-postgres.sh", "postgres-auth", "postgres", "password", "auth_db", "5432", "uvicorn", "auth_service:auth_service", "--host", "0.0.0.0", "--port", "9100"]
