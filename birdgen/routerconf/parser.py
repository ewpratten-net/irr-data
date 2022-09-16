from dataclasses import dataclass, field
import re
import os
from typing import List, Optional

from birdgen.whois.irr_routes import Routes, get_routes_for_as_set, get_routes_for_asn

# The basic definition of a router and neighbor addresses
_routerconf_re_stmnt = r"@routerconf peer (AS\d+) from (\d+\.\d+\.\d+\.\d+) at {\s*((?:[\d\.:a-z]+,? ?)+)\s*}"
# The possible flags
_routerconf_re_stmnt += r"\s?(requires-password)?"
_routerconf_re_stmnt += r"\s?(?:uses-private-as (\d+))?"
_routerconf_re_stmnt += r"\s?(?:override-own-as (\d+))?"
_routerconf_re_stmnt += r"\s?(?:name ([A-Za-z_]+))?"
_routerconf_re_stmnt += r"\s?(multihop)?"
_routerconf_re_stmnt += r"\s?(add-paths)?"
_routerconf_re_stmnt += r"\s?(extended-nexthop)?"

# Compile
ROUTERCONF_RE = re.compile(_routerconf_re_stmnt)


@dataclass
class RouterconfStatement:
    peer_as: int
    own_as: int
    own_router_id: str
    name: str
    multihop: bool
    add_paths: bool
    extended_nexthop: bool
    peer_neighbor_ips: List[str]
    password: Optional[str] = field(default=None)
    rewrite_as_to: Optional[int] = field(default=None)

    def get_peer_allowed_routes(self) -> Routes:
        return get_routes_for_as_set(self.policy["import"])
    
    def get_allowed_routes_for_export(self) -> Routes:
        return get_routes_for_as_set(self.policy["export"])


def parse_routerconf_line(raw_line: str, own_as: int) -> RouterconfStatement:

    # Parse the line
    matches = ROUTERCONF_RE.match(raw_line)

    # Build the statement
    return RouterconfStatement(
        peer_as=int(matches.group(1).replace("AS", "")
                    ) if not matches.group(5) else matches.group(5),
        own_as=int(matches.group(6)) if matches.group(6) else own_as,
        own_router_id=matches.group(2),
        name=matches.group(7) if matches.group(7) else matches.group(1),
        multihop=matches.group(8) is not None,
        add_paths=matches.group(9) is not None,
        extended_nexthop=matches.group(10) is not None,
        peer_neighbor_ips=[x.strip() for x in matches.group(3).split(",")],
        password=os.environ[f"PEER_PASS_{matches.group(1).upper()}"] if matches.group(
            4) else None,
        rewrite_as_to=int(matches.group(1).replace(
            "AS", "")) if matches.group(5) else None
    )
