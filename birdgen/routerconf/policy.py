import re
import string
from typing import Dict, Generator, List, Tuple
from birdgen.routerconf.parser import RouterconfStatement, parse_routerconf_line
from birdgen.whois.whois import make_whois_query

MP_IMPORT_PARSER = re.compile(
    r"afi ([a-z\.]+) from (AS[A-Za-z\d\-:]+)\s+accept ([A-Za-z\d\-:]+)")
MP_EXPORT_PARSER = re.compile(
    r"afi ([a-z\.]+) to (AS[A-Za-z\d\-:]+)\s+announce ([A-Za-z\d\-:]+)")

def linewise_whois(query: str, source: str) -> Generator[Tuple[str, str], None, None]:
    data = make_whois_query(query, source)

    # Placeholder for the current output data
    cur_key = ""
    cur_value = ""

    for line in data.split("\n"):

        # Skip empty lines
        if not line:
            continue

        # If the line dows not start with a character, it is a continuation of the previous line
        if line[0] not in string.ascii_lowercase:
            if len(cur_value) and cur_value[-1] != " ":
                cur_value += " "
            cur_value += line.strip()
            continue

        # Skip any line thats just an empty value
        if len(line.split(":")) == 1:
            continue

        # Otherwise, we must output the last line and start building the new one
        yield (cur_key, cur_value)
        cur_key, cur_value = line.strip().split(":", 1)
        cur_value = cur_value.strip()

    # Output the last line
    yield (cur_key, cur_value)


def get_route_policy(auth_num_obj: List[Tuple[str, str]], peer_asn: int) -> dict:
    output = {
        "import": None,
        "export": None,
        "afi": None
    }

    # Search the object for the route policy
    for line in auth_num_obj:

        # Handle import vs export
        if line[0] == "mp-import":
            matches = MP_IMPORT_PARSER.match(line[1])
            pol_afi = matches.group(1)
            pol_peer_asn = matches.group(2)
            pol_as_set = matches.group(3)
        elif line[0] == "mp-export":
            matches = MP_EXPORT_PARSER.match(line[1])
            pol_afi = matches.group(1)
            pol_peer_asn = matches.group(2)
            pol_as_set = matches.group(3)
        else:
            continue

        # If the peer ASN is the one we are looking for, add it to the output
        if pol_peer_asn == f"AS{peer_asn}" or pol_peer_asn == f"AS-ANY":
            output["afi"] = pol_afi
            if line[0] == "mp-import" and output["import"] is None:
                output["import"] = pol_as_set
            elif line[0] == "mp-export" and output["export"] is None:
                output["export"] = pol_as_set

    return output


def build_router_peer_data(own_as: int, auth_num_obj: List[Tuple[str, str]]) -> Dict[str, List[RouterconfStatement]]:
    output = {}

    for line in auth_num_obj:

        # Only process remarks
        if line[0] == "remarks":
            # Only process @routerconf remarks
            if line[1].startswith("@routerconf"):

                # Parse into a routerconf line
                parsed = parse_routerconf_line(line[1], own_as)

                # Add to the dictionary
                output.setdefault(parsed.own_router_id, []).append(parsed)

                # # Parse into parts
                # matches = ROUTERCONF_PARSER.match(line[1])

                # # Get the data
                # peer_as = matches.group(1)
                # router_id = matches.group(2)
                # peer_ips = [x.strip() for x in matches.group(3).split(",")]
                # requires_password = matches.group(4) is not None
                # rewrite_from = matches.group(5)
                # rewrite_to = matches.group(6)
                # name = matches.group(7)
                # multihop = matches.group(8) is not None
                # many_as = matches.group(9) is not None

                # # Add the data to the output
                # output.setdefault(router_id, []).append({
                #     "peer": int(peer_as.replace("AS", "")),
                #     "name": name,
                #     "ips": peer_ips,
                #     "requires_password": requires_password,
                #     "rewrite_from": int(rewrite_from) if rewrite_from else None,
                #     "rewrite_to": int(rewrite_to) if rewrite_to else None,
                #     "policy": get_route_policy(auth_num_obj, int(rewrite_to if rewrite_to else peer_as.replace("AS", ""))),
                #     "multihop": multihop,
                #     "many_as": many_as
                # })

    return output
