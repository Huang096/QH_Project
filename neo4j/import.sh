#!/bin/sh

set -e

# Set the password
neo4j-admin set-initial-password $NEO4J_PASSWORD

# Start server
neo4j start

# Wait for server to start
while [ -z "$(grep 'Started.' /var/lib/neo4j/logs/neo4j.log)" ]
do
  echo Waiting for neo4j to start
  sleep 1
done


# Import data
cat /var/lib/neo4j/import/import.cypher | cypher-shell -u $NEO4J_USERNAME -p $NEO4J_PASSWORD --format plain

# Stop server
neo4j stop
