#!/usr/bin/env sh

DB_URL="https://consensus.siahub.info/consensus.db.gz"
DB_FILE="consensus/consensus.db"

echo "Downloading updated Consensus..."
mkdir -p consensus
curl -L ${DB_URL} | gzip -dc > ${DB_FILE}

# Run sockat to listen 0.0.0.0:8000 and redirect to localhost:9980
socat tcp-listen:8000,reuseaddr,fork tcp:localhost:9980 &

siad --sia-directory `pwd`
