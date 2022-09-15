#! /bin/bash
set -e

# RTR001
echo "Handling RTR001"
scp -4 ./scripts/on-router/backbone_gre.sh rtr001-toronto-ca.net.va3zza.com:/usr/local/bin/backbone_gre.sh
scp -4 ./pathvector/build/rtr001.yml rtr001-toronto-ca.net.va3zza.com:/etc/pathvector.yml
ssh -4 rtr001-toronto-ca.net.va3zza.com " \
chmod +x /usr/local/bin/backbone_gre.sh; \
mkdir -p /var/www/html/pathvector; \
pathvector g -v
"

# RTR005
echo "Handling RTR005"
scp -4 ./scripts/on-router/backbone_gre.sh rtr005-frankfurt-de.net.va3zza.com:/usr/local/bin/backbone_gre.sh
scp -4 ./pathvector/build/rtr005.yml rtr005-frankfurt-de.net.va3zza.com:/etc/pathvector.yml
ssh -4 rtr005-frankfurt-de.net.va3zza.com " \
chmod +x /usr/local/bin/backbone_gre.sh; \
mkdir -p /var/www/html/pathvector; \
pathvector g -v
"