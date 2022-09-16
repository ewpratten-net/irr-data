
from typing import List
import re
from birdgen.whois.whois import make_whois_query

AS_SET_SEARCH_RE = re.compile(r"(?:AS(\d+)\s?)")

def expand_as_set(as_set: str) -> List[int]:
    print(f"Expanding AS-SET: {as_set}")
    
    # Make a whois query
    data = make_whois_query(f"!i{as_set},1")
    
    # Find the AS numbers
    ases = []
    for line in data.splitlines():
        matches = AS_SET_SEARCH_RE.findall(line)
        
        if matches:
            ases.extend([int(asn) for asn in matches])
    
    return ases
    