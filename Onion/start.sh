#!/bin/sh
docker build -t torwebnew . && \
ID=$(docker run -d -p 4242:4242 -v tor-hidden-service:/var/lib/tor/hidden_service torwebnew) && \
echo "Container $ID launched. Generating the address..." && \
until docker exec $ID test -f /var/lib/tor/hidden_service/hostname; do sleep 1; done && \
echo -e "\n.Onion address :" && \
docker exec $ID cat /var/lib/tor/hidden_service/hostname