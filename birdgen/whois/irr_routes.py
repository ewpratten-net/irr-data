
from dataclasses import dataclass
import subprocess
from typing import List
import re
from birdgen.whois.whois import make_whois_query

PREFIX_LIST_RE = re.compile(r"^([\d\.:a-z\/\s]+)")
PREFIX_LIST_MESSY_RE = re.compile(r"([\d\.:a-z\/\s]+)")


@dataclass
class Routes:
    ipv4: List[str]
    ipv6: List[str]


def get_routes_for_asn(asn: int) -> Routes:
    print(f"Getting routes that may be originated by: {asn}")

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
    out = Routes([], [])
    for prefix in prefix_list:
        if ":" in prefix:
            out.ipv6.append(prefix)
        else:
            out.ipv4.append(prefix)

    return out


as_set_cache = {}


def get_routes_for_as_set(as_set: str) -> Routes:
    print(f"Getting routes that may be originated by members of: {as_set}")

    if not as_set:
        return Routes([], [])

    if as_set == "ANY":
        data = Routes(
            ["0.0.0.0/0{0,32}"],
            ["::/0{0,128}"]
        )
        as_set_cache[as_set] = data
        return data

    # hit the cache
    if as_set in as_set_cache:
        return as_set_cache[as_set]

    # Run BGPq4 to get the routes
    data = subprocess.Popen(
        ["bgpq4", "-b4", as_set], stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
    data += subprocess.Popen(["bgpq4", "-b6", as_set],
                             stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
    data = data.replace("\n", " ")

    # Find prefixes
    matches = PREFIX_LIST_MESSY_RE.findall(data)
    prefix_list = [match.strip() for match in matches]

    # Reformat into a routes object
    out = Routes([], [])
    for prefix in prefix_list:
        if ":" in prefix:
            out.ipv6.append(prefix)
        elif "." in prefix:
            out.ipv4.append(prefix)

    # Cache the result
    as_set_cache[as_set] = out
    return out
