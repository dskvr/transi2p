#!/bin/bash
#setup IP tables

# sudo /var/lib/transi2p/transi2p/rules.sh

# sudo mkdir -p /etc/iptables
# sudo touch /etc/iptables/iptables.rules
# sudo iptables-legacy-save > /etc/iptables/iptables.rules

# sudo useradd -m -s /usr/sbin/nologin -d /var/lib/transi2p transi2p

# sudo -u transi2p twistd -d /var/lib/transi2p \
#                         --pidfile=/var/lib/transi2p/twistd.pid \
#                         --logfile /dev/null transi2p -c /etc/transi2p/config.json 

# useradd -m -s /usr/sbin/nologin -d /var/lib/transi2p transi2p

touch /var/log/transi2p/twistd.log
chown transi2p:transi2p /var/log/transi2p/twistd.log

# twistd -d /var/lib/transi2p \
#         --pidfile=/var/lib/transi2p/twistd.pid \
#         --logfile /var/log/transi2p/transi2p.log transi2p -c /etc/transi2p/config.json \

# twistd -n transi2p \
#         --pidfile=/var/lib/transi2p/twistd.pid \
#         --logfile /var/log/transi2p/transi2p.log transi2p -c /etc/transi2p/config.json \
        

# #run twisted 
twistd -n transi2p -c /etc/transi2p/config.json