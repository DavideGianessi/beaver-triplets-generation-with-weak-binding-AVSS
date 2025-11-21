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
#  router:
#    build: ./router
#    container_name: router
#    environment:
#      - N_PARTIES=$N
#    networks:
#      mpcnet:
#        ipv4_address: 172.20.0.9
#    volumes:
#      - ./outputs:/outputs
EOF


for i in $(seq 1 $N ); do
  ip=$((10 + i))
  cat >> docker-compose.yml <<EOF

  party$i:
    build: ./party
    container_name: party$i
    environment:
      - PARTY_ID=$i
      - N_PARTIES=$N
      - MODULUS=$MODULUS
      - ROUTER_HOST=router
      - MAIN=$PROTOCOL
      - GRACE_PERIOD=20
      - AMOUNT=$AMOUNT
    networks:
      mpcnet:
        ipv4_address: 172.20.$((ip / 256)).$((ip % 256))
    volumes:
      - ./outputs:/outputs
EOF
done

cat >> docker-compose.yml <<EOF

networks:
  mpcnet:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
EOF

echo "[*] Generated docker-compose.yml with $N parties."
docker-compose up --build --remove-orphans
