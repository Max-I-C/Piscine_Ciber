# Image Alpine for nginx (super light)
FROM alpine:3.21
RUN apk add --no-cache nginx tor
RUN mkdir -p /var/www/html /var/lib/tor/hidden_service /run/nginx

COPY /index.html /var/www/html
COPY /conf/nginx.conf /etc/nginx/nginx.conf
COPY /conf/torrc /etc/tor/torrc 

RUN chown -R nginx:nginx /var/www/html
RUN chown -R tor:tor /var/lib/tor

CMD ["sh", "-c", "su tor -c 'tor -f /etc/tor/torrc --RunAsDaemon 0' & nginx -g 'daemon off;' && wait"]