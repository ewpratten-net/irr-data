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
_routerconf_re_stmnt += r"\s?(?:prepend (\d+)\s?(\d+)?)?"
_routerconf_re_stmnt += r"\s?(?:prepend-private (\d+)\s?(\d+)?)?"
_routerconf_re_stmnt += r"\s?(?:export-communities ([\d:\s]+))?"
_routerconf_re_stmnt += r"\s?(?:drop-peer-downstreams ([\d\s]+))?"

# Compile
print(f"Compiling routerconf RE: {_routerconf_re_stmnt}")
ROUTERCONF_RE = re.compile(_routerconf_re_stmnt)


@dataclass
class RouterconfStatement:
    peer_as: int
    public_asn: int
    own_as: int
    own_router_id: str
    name: str
    multihop: bool
    add_paths: bool
    extended_nexthop: bool
    peer_neighbor_ips: List[str]
    prepend_in: range
    prepend_out: range
    prepend_in_private: range
    prepend_out_private: range
    export_communities: List[str]
    export_large_communities: List[str]
    drop_ases: List[int]
    password: Optional[str] = field(default=None)
    rewrite_as_to: Optional[int] = field(default=None)

    def get_peer_allowed_routes(self) -> Routes:
        return get_routes_for_as_set(self.policy["import"])

    def get_allowed_routes_for_export(self) -> Routes:
        return get_routes_for_as_set(self.policy["export"])


def parse_routerconf_line(raw_line: str, own_as: int) -> RouterconfStatement:

    # Parse the line
    matches = ROUTERCONF_RE.match(raw_line)

    communities_out = matches.group(15).split(" ") if matches.group(15) else []
    # print(matches.group(0))
    
    # Build the statement
    return RouterconfStatement(
        peer_as=int(matches.group(1).replace("AS", "")
                    ) if not matches.group(5) else matches.group(5),
        public_asn=int(matches.group(1).replace("AS", "")),
        own_as=int(matches.group(6)) if matches.group(6) else own_as,
        own_router_id=matches.group(2),
        name=matches.group(7) if matches.group(7) else matches.group(1),
        multihop=matches.group(8) is not None,
        add_paths=matches.group(9) is not None,
        extended_nexthop=matches.group(10) is not None,
        peer_neighbor_ips=[x.strip() for x in matches.group(3).split(",")],
        password=os.environ[f"PEER_PASS_{matches.group(1).upper()}"] if matches.group(
            4) else None,
        rewrite_as_to=None,
        prepend_in=range(int(matches.group(11)) if matches.group(11) else 0),
        prepend_out=range(int(matches.group(12)) if matches.group(
            12) else int(matches.group(11)) if matches.group(11) else 0),
        prepend_in_private=range(
            int(matches.group(13)) if matches.group(13) else 0),
        prepend_out_private=range(int(matches.group(14)) if matches.group(
            14) else int(matches.group(13)) if matches.group(13) else 0),
        export_communities=[x.strip().replace(":", ",")
                            for x in communities_out if len(x.split(":")) == 2],
        export_large_communities=[x.strip().replace(":", ",")
                                  for x in communities_out if len(x.split(":")) == 3],
        drop_ases=[int(x.strip()) for x in matches.group(16).split(" ")] if matches.group(16) else [],
    )
