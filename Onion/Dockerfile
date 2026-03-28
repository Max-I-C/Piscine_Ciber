# Image Alpine for nginx (super light)
FROM alpine:3.21
RUN apk add --no-cache nginx tor
RUN mkdir -p /var/www/html /var/lib/tor/hidden_service /run/nginx /run/tor

COPY /index.html /var/www/html
COPY /conf/nginx.conf /etc/nginx/nginx.conf
COPY /conf/torrc /etc/tor/torrc 

RUN chown -R nginx:nginx /var/www/html
RUN chown -R tor:tor /var/lib/tor /run/tor && chmod 700 /var/lib/tor && chmod 755 /var/lib/tor/hidden_service

VOLUME ["/var/lib/tor/hidden_service"]

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]