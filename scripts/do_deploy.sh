#! /bin/bash
set -e

IPTABLES_BLOCKLIST="\
iptables -A INPUT -s 61.177.172.0 -j DROP; \
iptables -A INPUT -s 61.177.173.0 -j DROP; \
iptables -A INPUT -s 122.117.51.0 -j DROP; \
"

# RTR001
echo "Handling RTR001"
scp -4 ./scripts/on-router/backbone_gre.sh rtr001-toronto-ca.net.va3zza.com:/usr/local/bin/backbone_gre.sh
scp -4 ./gen/74.119.150.163.conf rtr001-toronto-ca.net.va3zza.com:/etc/bird/bird.conf
scp -4 ./router-config/netplan/rtr001/60-ewpratten-net.yaml rtr001-toronto-ca.net.va3zza.com:/etc/netplan/60-ewpratten-net.yaml
ssh -4 rtr001-toronto-ca.net.va3zza.com " \
sysctl -w net.ipv6.conf.all.forwarding=1; \
sysctl -w net.ipv4.ip_forward=1; \
chmod +x /usr/local/bin/backbone_gre.sh; \
birdc c
"
ssh -4 rtr001-toronto-ca.net.va3zza.com $IPTABLES_BLOCKLIST

# RTR002
echo "Handling RTR002"
scp -4 ./scripts/on-router/backbone_gre.sh rtr002-nj-us.net.va3zza.com:/usr/local/bin/backbone_gre.sh
scp -4 ./gen/68.232.175.168.conf rtr002-nj-us.net.va3zza.com:/etc/bird/bird.conf
scp -4 ./router-config/netplan/rtr002/60-ewpratten-net.yaml rtr002-nj-us.net.va3zza.com:/etc/netplan/60-ewpratten-net.yaml
ssh -4 rtr002-nj-us.net.va3zza.com " \
sysctl -w net.ipv6.conf.all.forwarding=1; \
sysctl -w net.ipv4.ip_forward=1; \
chmod +x /usr/local/bin/backbone_gre.sh; \
birdc c
"
ssh -4 rtr002-nj-us.net.va3zza.com $IPTABLES_BLOCKLIST

# RTR004
echo "Handling RTR004"
scp -4 ./scripts/on-router/backbone_gre.sh rtr004-fremont-us.net.va3zza.com:/usr/local/bin/backbone_gre.sh
scp -4 ./gen/134.195.121.110.conf rtr004-fremont-us.net.va3zza.com:/etc/bird/bird.conf
scp -4 ./router-config/netplan/rtr004/60-ewpratten-net.yaml rtr004-fremont-us.net.va3zza.com:/etc/netplan/60-ewpratten-net.yaml
ssh -4 rtr004-fremont-us.net.va3zza.com " \
sysctl -w net.ipv6.conf.all.forwarding=1; \
sysctl -w net.ipv4.ip_forward=1; \
chmod +x /usr/local/bin/backbone_gre.sh; \
birdc c
"
ssh -4 rtr004-fremont-us.net.va3zza.com $IPTABLES_BLOCKLIST

# RTR005
echo "Handling RTR005"
ssh -4 rtr005-frankfurt-de.net.va3zza.com "rm -rf /var/log/journal/**/*"
scp -4 ./scripts/on-router/backbone_gre.sh rtr005-frankfurt-de.net.va3zza.com:/usr/local/bin/backbone_gre.sh
scp -4 ./gen/193.148.249.164.conf rtr005-frankfurt-de.net.va3zza.com:/etc/bird/bird.conf
scp -4 ./router-config/netplan/rtr005/60-ewpratten-net.yaml rtr005-frankfurt-de.net.va3zza.com:/etc/netplan/60-ewpratten-net.yaml
ssh -4 rtr005-frankfurt-de.net.va3zza.com " \
sysctl -w net.ipv6.conf.all.forwarding=1; \
sysctl -w net.ipv4.ip_forward=1; \
chmod +x /usr/local/bin/backbone_gre.sh; \
birdc c
"
ssh -4 rtr005-frankfurt-de.net.va3zza.com $IPTABLES_BLOCKLIST