#!/bin/bash

# Write variables to a .env file
echo "MILVUS_IP=$MILVUS_IP" > /.env
# shellcheck disable=SC2129
echo "MILVUS_PORT=$MILVUS_PORT" >> /.env

# Export .env file location
export ENV_FILE_LOCATION=/.env

cat /.env

# Install netcat
apt-get update
apt-get install -y netcat-openbsd

# Loop until milvus service is available. It should be available as the backend depends on it
max_retries=10
retry_count=0

while ! nc -z "$MILVUS_IP" "$MILVUS_PORT" && [ "$retry_count" -lt "$max_retries" ]; do
  echo "Milvus service not available. Retrying in 5 seconds..."
  sleep 5
  ((retry_count++))
done

if [ "$retry_count" -eq "$max_retries" ]; then
  echo "Failed to connect to Milvus service after $max_retries attempts."
  exit
else
  echo "Milvus service is available at $MILVUS_IP:$MILVUS_PORT."
fi

# Create default database
echo "Creating default database..."
python -m src.db_utilities.create_database

echo "Starting backend..."

# Start the backend
uvicorn src.app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload --log-level critical
