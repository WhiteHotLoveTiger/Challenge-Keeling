#!/bin/bash

# This file is a convenience wrapper around the docker container for sending
# graph queries. You can send json queries via stdin to this file like this:
# $ cat my_query.json | ./query.sh


CONTAINER_NAME="graph_info"

# Check if the container is running
if [[ $(docker ps --quiet --filter name=$CONTAINER_NAME) ]]; then
    docker exec -i $CONTAINER_NAME python src/query_service/query_listener.py
else
    echo "Container '$CONTAINER_NAME' is not running."
    echo "Starting the container..."
    docker compose up -d
    echo "Container started. Now attaching to the query listener service..."
    docker exec -i $CONTAINER_NAME python src/query_service/query_listener.py
    docker compose down
fi
