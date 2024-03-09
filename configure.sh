#!/bin/sh
# sudo su - transi2p

# sudo iptables -L -n

/var/lib/transi2p/rules.sh

mkdir -p /etc/iptables
touch /etc/iptables/iptables.rules
iptables-legacy-save > /etc/iptables/iptables.rules

# sudo useradd -m -s /usr/sbin/nologin -d /var/lib/transi2p transi2p

# sudo -u transi2p twistd -d /var/lib/transi2p \
#                         --pidfile=/var/lib/transi2p/twistd.pid \
#                         --logfile /dev/null transi2p -c /etc/transi2p/config.json 