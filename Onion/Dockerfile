# Image Alpine for nginx (super light)
FROM alpine:3.21
RUN apk add --no-cache nginx tor openssh
RUN mkdir -p /var/www/html /var/lib/tor/hidden_service /var/run/sshd /run/nginx /run/tor

RUN ssh-keygen -A

COPY /index.html /var/www/html
COPY /conf/nginx.conf /etc/nginx/nginx.conf
COPY /conf/torrc /etc/tor/torrc 
COPY /conf/sshd_config /etc/ssh/sshd_config

RUN adduser -D user && echo "user:password" | chpasswd

RUN chown -R nginx:nginx /var/www/html
RUN chown -R tor:tor /var/lib/tor /run/tor && chmod 700 /var/lib/tor && chmod 755 /var/lib/tor/hidden_service

VOLUME ["/var/lib/tor/hidden_service"]

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80 4242

ENTRYPOINT ["/entrypoint.sh"]