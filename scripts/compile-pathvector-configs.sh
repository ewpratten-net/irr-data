#! /bin/bash
set -e

# Ensure the build directory exists
mkdir -p pathvector/build

# Save the routerconf data for processing
routerconf_json=$(python3 scripts/autnum-routerconf-parser.py AS398057 --aut-num-source-db whois.altdb.net)

# Handle each base config
for config in pathvector/router/*.yml; do
    name=$(basename "$config" .yml)
    echo "Building: $name"
    
    # Get this config's router id
    router_id=$(cat $config | python3 -m yq '.["router-id"]')
    echo "Router ID: $router_id"
    
    # Concat base data into a single file
    cat "$config" pathvector/base.yml > pathvector/build/"$name".yml
    
    # Send the routerconf data to python to convert into more yml
    echo "$routerconf_json" | python3 -c "\
import json, sys
data = json.load(sys.stdin)
router_id = $router_id
print('\npeers:')
for peer in data['neighbors'][router_id]:
    print(
        '''  {name}:
    asn: {asn}
    template: peer
    neighbors:'''.format(
        name=peer['name'].lower() if peer['name'] else 'as' + str(peer['peer']),
        asn=peer['peer'],
    ))
    for neighbor in peer['ips']:
        print(f'      - {neighbor}')
    if peer['policy']['import']:
        print('    as-set: ' + peer['policy']['import'])
    " >> pathvector/build/"$name".yml
done