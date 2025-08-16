#!/bin/bash
set -euo pipefail

echo "--------------------------------------------------------------"
echo "starting nats broker..."

# Download from source b/c snap's version is too old (doesn't have jetstream support)
curl -L https://github.com/nats-io/nats-server/releases/download/v2.6.6/nats-server-v2.6.6-linux-amd64.zip -o nats-server.zip

unzip nats-server.zip -d nats-server

nats-server/nats-server-v2.6.6-linux-amd64/nats-server -js >>broker.out 2>&1 &

echo "--------------------------------------------------------------"
echo "waiting for nats broker..."
sleep 15
