#! /bin/bash
# Usage: backbone_gre.sh <local_ip> <local_router_id> <remote_ip> <remote_router_id>
set -ex

# Validate input
if [ $# -ne 4 ]; then
    echo "Usage: backbone_gre.sh <local_ip> <local_router_id> <remote_ip> <remote_router_id>"
    exit 1
fi

# Sum the two router ids
combined_rid=$(($2 + $4))
combined_rid_hex=$(python3 -c "print(hex($combined_rid)[2:])")

# Name a new tunnel interface
TUN_NAME=backbone$combined_rid

# Try to delete the link if it exists
ip link del $TUN_NAME || true
ip link del bbone-dummy || true

# Bring up a gre tunnel
ip link add $TUN_NAME type gretap local $1 remote $3 ttl 255
ip link set dev $TUN_NAME up
ip addr flush dev $TUN_NAME

# Bring up a dummy interface for announcing the whole backbone addr space
ip link add bbone-dummy type dummy
ip link set dev bbone-dummy up
ip addr add 2a06:a005:5a6::/48 dev bbone-dummy

# Use a predictable link-local address
ip addr add fe80:246:0:$combined_rid_hex::$2/64 dev $TUN_NAME

# Add non-link-local addresses
ip addr add 2a12:dd47:9001:0:$combined_rid_hex::$2/80 dev $TUN_NAME

# We need a static route for the peer on some hosts
ip -6 route add 2a12:dd47:9001:0:$combined_rid_hex::$4/128 dev $TUN_NAME

ip6tables -A FORWARD -i $TUN_NAME -j ACCEPT
ip6tables -A FORWARD -o $TUN_NAME -j ACCEPT
