import argparse
import re
import string
import subprocess
import sys
import json
from typing import Generator, List, Tuple

DEFAULT_IRR_DB = "whois.radb.net"
ROUTERCONF_PARSER = re.compile(
    r"@routerconf peer (AS\d+) from (\d+\.\d+\.\d+\.\d+) at {\s*((?:[\d\.:a-z]+,?)+)\s*}\s?(requires-password)?\s?(?:rewrite (\d+) (\d+))?")
MP_IMPORT_PARSER = re.compile(
    r"afi ([a-z\.]+) from (AS[A-Za-z\d\-:]+)\s+accept ([A-Za-z\d\-:]+)")
MP_EXPORT_PARSER = re.compile(
    r"afi ([a-z\.]+) to (AS[A-Za-z\d\-:]+)\s+announce ([A-Za-z\d\-:]+)")


def log(*args):
    print(*args, file=sys.stderr)


def raw_whois(query: str, source: str) -> str:
    proc = subprocess.Popen(
        ["whois", "-h", source, query], stdout=subprocess.PIPE)
    return proc.communicate()[0].decode("utf-8")


def linewise_whois(query: str, source: str) -> Generator[Tuple[str, str], None, None]:
    data = raw_whois(query, source)

    # Placeholder for the current output data
    cur_key = ""
    cur_value = ""

    for line in data.split("\n"):

        # Skip empty lines
        if not line:
            continue

        # If the line dows not start with a character, it is a continuation of the previous line
        if line[0] not in string.ascii_lowercase:
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
        "export": None
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
            if line[0] == "mp-import" and output["import"] is None:
                output["import"] = pol_as_set
            elif line[0] == "mp-export" and output["export"] is None:
                output["export"] = pol_as_set

    return output


def build_router_peer_data(auth_num_obj: List[Tuple[str, str]]) -> dict:
    output = {}

    for line in auth_num_obj:

        # Only process remarks
        if line[0] == "remarks":
            # Only process @routerconf remarks
            if line[1].startswith("@routerconf"):

                # Parse into parts
                matches = ROUTERCONF_PARSER.match(line[1])

                # Get the data
                peer_as = matches.group(1)
                router_id = matches.group(2)
                peer_ips = matches.group(3).split(",")
                requires_password = matches.group(4) is not None
                rewrite_from = matches.group(5)
                rewrite_to = matches.group(6)

                # Add the data to the output
                output.setdefault(router_id, []).append({
                    "peer": int(peer_as.replace("AS", "")),
                    "ips": peer_ips,
                    "requires_password": requires_password,
                    "rewrite_from": int(rewrite_from) if rewrite_from else None,
                    "rewrite_to": int(rewrite_to) if rewrite_to else None,
                    "policy": get_route_policy(auth_num_obj, int(peer_as.replace("AS", "")))
                })

    return output


def main() -> int:
    # Handle program arguments
    ap = argparse.ArgumentParser(
        description='Converts @routerconf data in aut-num objects to JSON')
    ap.add_argument("aut_num", help="Aut-num to parse")
    ap.add_argument("--aut-num-source-db",
                    help="Override the source IRR database for the aut-num")
    args = ap.parse_args()

    # Get the raw whois data for the aut-num
    aut_num_obj = list(linewise_whois(
        args.aut_num, args.aut_num_source_db or DEFAULT_IRR_DB))

    # Build the output
    out = {
        "neighbors": build_router_peer_data(aut_num_obj)
    }

    print(json.dumps(out, indent=4))

    return 0


if __name__ == "__main__":
    sys.exit(main())
