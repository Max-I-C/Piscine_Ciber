#!/bin/sh
set -e

# Fix permissions for mounted volume
chown -R tor:tor /var/lib/tor/hidden_service
chmod 700 /var/lib/tor/hidden_service

# Start Tor as tor user
su tor -s /bin/sh -c "tor -f /etc/tor/torrc --RunAsDaemon 0" &

# Start nginx as root
exec nginx -g 'daemon off;'
