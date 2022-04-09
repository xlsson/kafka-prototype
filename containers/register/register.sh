#!/usr/bin/env bash
# Register the Debezium connector specified in the environment variables

# JSON connection string, using environment variables provided in docker-compose/k8s-config file
CONNECTIONSTRING='{ "name": "'$CONNECTORNAME'", "config": { "connector.class": "io.debezium.connector.sqlserver.SqlServerConnector", "database.hostname": "'$DBHOSTNAME'", "database.port": "'$DBPORT'", "database.user": "'$DBUSER'", "database.password": "'$DBPASSWORD'", "database.dbname": "'$DBNAME'", "database.server.name": "'$SERVERNAME'", "table.include.list": "'$TABLEINCLUDELIST'", "database.history.kafka.bootstrap.servers": "'$DBHISTBOOTSTRAPSERVERS'", "database.history.kafka.topic": "'$DBHISTTOPIC'" }}'

# Default SERVER to "localhost" if SERVER environment variable is empty
if [ -z "$SERVER" ]; then
    SERVER='localhost'
fi

echo "SERVER is set to: $SERVER"

CREATED='201 Created'
EXISTS='409 Conflict'
ATTEMPTS=0

function sendRequest
{
    ATTEMPTS=$((ATTEMPTS+1))
    echo "Attempting to register connector. Attempt nr: $ATTEMPTS"

    # POST request to Debezium API to register connector
    result=$(curl --silent -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" "$SERVER":8083/connectors/ -d "$CONNECTIONSTRING")

    if [[ "$result" == *"$CREATED"* ]] || [[ "$result" == *"$EXISTS"* ]]; then
        # Display result and list of connectors    
        connectors=$(curl --silent -H "Accept:application/json" "$SERVER":8083/connectors/)
        printf "%s\\n" "" "$result" "$connectors"
        exit 0
    else
        # Call sendRequest again
        printf "%s\\n" "" "Unsuccessful attempt, next attempt in 3 seconds" ""
        sleep 3
        sendRequest
    fi
}

# Initiate first attempt to send request
sendRequest