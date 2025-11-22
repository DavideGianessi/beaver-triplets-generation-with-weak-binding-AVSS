#!/bin/bash
set -e

N=${1:-5}

MODULUS=170141183460469231731687303715884105727   #2^127-1
#MODULUS=227

PROTOCOL=${2:-test}

AMOUNT=${3:-1}

mkdir -p ./outputs

cat > docker-compose.yml <<EOF
services:
  mpc:
    build: ./party
    container_name: mpc
    environment:
      - N_PARTIES=$N
      - MODULUS=$MODULUS
      - MAIN=$PROTOCOL
      - GRACE_PERIOD=5
      - AMOUNT=$AMOUNT
      - BASE_PORT=5000
    volumes:
      - ./outputs:/outputs
EOF

echo "[*] Generated docker-compose.yml with $N parties."
docker-compose up --build --remove-orphans
