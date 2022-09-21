
import re
from typing import List
import requests

BANNED_COUNTRY_CODES = [
    "RU",
    "CN",
    "KP"
]
ASN_PARSE = re.compile(r"\/AS(\d+)")


def get_banned_asn_list() -> List[int]:

    output = []
    
    print("Querying banned countries for ASNs")
    for country in BANNED_COUNTRY_CODES:
        print(f"Querying {country}")
        response = requests.get(f"https://bgp.he.net/country/{country.upper()}", headers={
                                "User-Agent": "AS398057 Config Updater"})

        if response.status_code != 200:
            print(
                f"Failed to get ASN list for {country}. Status code: {response.status_code}")
            continue
        
        # Parse the ASN list
        for line in response.text.splitlines():
            match = ASN_PARSE.search(line)
            if match:
                output.append(int(match.group(1)))
                
    # Sort and remove duplicates
    print(f"Found {len(output)} banned ASNs")
    output.sort()
    output = list(dict.fromkeys(output))
    print(f"After deduplication, {len(output)} ASNs remain")

    return output
