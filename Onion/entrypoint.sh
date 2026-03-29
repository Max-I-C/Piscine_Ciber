#!/bin/sh
set -e

# Ensure runtime directory exists for sshd
mkdir -p /var/run/sshd

# Fix permissions for mounted volume
chown -R tor:tor /var/lib/tor/hidden_service
chmod 700 /var/lib/tor/hidden_service

# Start Tor as tor user
su tor -s /bin/sh -c "tor -f /etc/tor/torrc --RunAsDaemon 0" &

# Start OpenSSH daemon in background
/usr/sbin/sshd

# Start nginx as root
exec nginx -g 'daemon off;'
