
from dataclasses import dataclass
from typing import List
import re
from birdgen.whois.whois import make_whois_query

PREFIX_LIST_RE = re.compile(r"^([\d\.:a-z\/\s]+)")

@dataclass
class Routes:
    ipv4: List[str]
    ipv6: List[str]
    
def get_routes_for_asn(asn: int) -> Routes:
    
    # Make a whois query for IPv4 prefixes and append a query for IPv6 prefixes
    data = make_whois_query(f"!gAS{asn}")
    data += make_whois_query(f"!6AS{asn}")
    
    # Find the prefix list
    prefix_list = []
    for line in data.splitlines():
        match = PREFIX_LIST_RE.match(line)
        if match:
            prefix_list.extend(match.group(1).split(" "))
            
    # Reformat into a routes object
    out = Routes([],[])
    for prefix in prefix_list:
        if ":" in prefix:
            out.ipv6.append(prefix)
        else:
            out.ipv4.append(prefix)

    return out