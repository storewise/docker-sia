#!/usr/bin/env bash

DB_URL="https://consensus.siahub.info/consensus.db.gz"
DB_FILE="consensus/consensus.db"

if [[ ! -f ${DB_FILE} ]]; then
    echo "Downloading updated Consensus..."
    mkdir -p consensus
    wget -q --progress=bar:noscroll --show-progress -O - ${DB_URL} | gzip -dc > ${DB_FILE}
fi

# Run sockat to listen 0.0.0.0:8000 and redirect to localhost:9980
socat tcp-listen:8000,reuseaddr,fork tcp:localhost:9980 &

siad --sia-directory `pwd`
