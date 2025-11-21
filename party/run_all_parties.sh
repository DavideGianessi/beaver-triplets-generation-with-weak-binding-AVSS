#!/bin/bash
set -e

N=${N_PARTIES:-5}

for ID in $(seq 1 $N); do
    echo "[*] Starting party $ID"
    PARTY_ID=$ID python party.py &
done

wait
