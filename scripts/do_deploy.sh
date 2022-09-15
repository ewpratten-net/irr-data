#! /bin/bash
set -e

# RTR001
echo "Handling RTR001"
scp -4 ./scripts/on-router/backbone_gre.sh rtr001-toronto-ca.net.va3zza.com:/usr/local/bin/backbone_gre.sh
scp -4 ./router-config/pathvector/build/rtr001.yml rtr001-toronto-ca.net.va3zza.com:/etc/pathvector.yml
scp -4 ./router-config/netplan/rtr001/60-ewpratten-net.yml rtr001-toronto-ca.net.va3zza.com:/etc/netplan/60-ewpratten-net.yml
ssh -4 rtr001-toronto-ca.net.va3zza.com " \
chmod +x /usr/local/bin/backbone_gre.sh; \
mkdir -p /var/www/html/pathvector; \
pathvector g -v
"

# RTR002
echo "Handling RTR002"
scp -4 ./scripts/on-router/backbone_gre.sh rtr002-toronto-ca.net.va3zza.com:/usr/local/bin/backbone_gre.sh
scp -4 ./router-config/pathvector/build/rtr002.yml rtr002-toronto-ca.net.va3zza.com:/etc/pathvector.yml
scp -4 ./router-config/netplan/rtr002/60-ewpratten-net.yml rtr002-toronto-ca.net.va3zza.com:/etc/netplan/60-ewpratten-net.yml
ssh -4 rtr002-toronto-ca.net.va3zza.com " \
chmod +x /usr/local/bin/backbone_gre.sh; \
mkdir -p /var/www/html/pathvector; \
pathvector g -v
"

# RTR004
echo "Handling RTR004"
scp -4 ./scripts/on-router/backbone_gre.sh rtr004-toronto-ca.net.va3zza.com:/usr/local/bin/backbone_gre.sh
scp -4 ./router-config/pathvector/build/rtr004.yml rtr004-toronto-ca.net.va3zza.com:/etc/pathvector.yml
scp -4 ./router-config/netplan/rtr004/60-ewpratten-net.yml rtr004-toronto-ca.net.va3zza.com:/etc/netplan/60-ewpratten-net.yml
ssh -4 rtr004-toronto-ca.net.va3zza.com " \
chmod +x /usr/local/bin/backbone_gre.sh; \
mkdir -p /var/www/html/pathvector; \
pathvector g -v
"

# RTR005
echo "Handling RTR005"
scp -4 ./scripts/on-router/backbone_gre.sh rtr005-frankfurt-de.net.va3zza.com:/usr/local/bin/backbone_gre.sh
scp -4 ./router-config/pathvector/build/rtr005.yml rtr005-frankfurt-de.net.va3zza.com:/etc/pathvector.yml
scp -4 ./router-config/netplan/rtr005/60-ewpratten-net.yml rtr005-frankfurt-de.net.va3zza.com:/etc/netplan/60-ewpratten-net.yml
ssh -4 rtr005-frankfurt-de.net.va3zza.com " \
chmod +x /usr/local/bin/backbone_gre.sh; \
mkdir -p /var/www/html/pathvector; \
pathvector g -v
"