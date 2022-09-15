#! /bin/bash
set -e

ROUTER_LINK_PREFIX=2a12:dd47:9001

# Ensure the build directory exists
mkdir -p router-config/pathvector/build

# Save the routerconf data for processing
routerconf_json=$(python3 scripts/autnum-routerconf-parser.py AS398057 --aut-num-source-db whois.altdb.net)

# Get the backbone link pairs
# BONE_LINK_NUMBERS=$(whois -h whois.altdb.net AS398057 | grep "remarks:\s*@backbonelink" | awk '{ print $3 " " $4 "|" }')

# Handle each base config
for config in router-config/pathvector/router/*.yml; do
    name=$(basename "$config" .yml)
    echo "Building: $name"
    
    # The router number is the name without "rtr"
    router_num=${name#rtr}
    
    # Get this config's router id
    router_id=$(cat $config | python3 -m yq '.["router-id"]')
    echo "Router ID: $router_id"
    
    # Concat base data into a single file
    cat "$config" router-config/pathvector/base.yml > router-config/pathvector/build/"$name".yml
    
    # Send the routerconf data to python to convert into more yml
    echo "$routerconf_json" | python3 -c "\
import json, sys, os
data = json.load(sys.stdin)
router_id = $router_id
print('\npeers:')
for peer in data['neighbors'][router_id]:
    peer_name = peer['name'].lower() if peer['name'] else 'as' + str(peer['peer'])
    print(
        '''  {name}:
    asn: {asn}
    template: peer
    neighbors:'''.format(
        name=peer_name,
        asn=peer['peer'],
    ))
    for neighbor in peer['ips']:
        print(f'      - {neighbor}')
    if peer['policy']['import']:
        print('    as-set: ' + peer['policy']['import'])
    if peer['requires_password']:
        print('    password: ' + os.environ['PEER_PASS_{}'.format(peer_name.upper())])
    if peer['multihop']:
        print('    multihop: true')
    " >> router-config/pathvector/build/"$name".yml

    
#     echo $BONE_LINK_NUMBERS | python3 -c "\
# import sys
# data = sys.stdin.read()
# for line in data.split('|'):
#     if not line.strip():
#         continue
#     num1, num2 = line.strip().split(' ',1)
#     nonlocal_router_num = num1 if num1 != '$router_num' else num2
#     nonlocal_asn = '4204466' + nonlocal_router_num

#     # If either of the numbers is the router number, add the link
#     if num1 == '$router_num' or num2 == '$router_num':
#         print(f'''  backbone-{num1}-{num2}:
#     local-asn: 4204466$router_num
#     asn: {nonlocal_asn}
#     template: backbone
#     neighbors:
#       - $ROUTER_LINK_PREFIX:0:{hex(int(num1) + int(num2))[2:]}::{int(nonlocal_router_num)}
#     ''')
#     " >> pathvector/build/"$name".yml
done