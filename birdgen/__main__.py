import argparse
from pathlib import Path
import sys
from birdgen.routerconf.policy import build_router_peer_data, linewise_whois
from jinja2 import Environment, PackageLoader, select_autoescape
from birdgen.whois.irr_routes import get_routes_for_asn


def main() -> int:
    # Handle program arguments
    ap = argparse.ArgumentParser(
        description='Generates BIRD configs from IRR data')
    ap.add_argument("asn", type=int, help="ASN to generate config for")
    ap.add_argument("-o", "--output", type=str, help="Output directory for generated configs", required=True)
    ap.add_argument("--aut-num-source-db",
                    help="Override the source IRR database for the aut-num")
    args = ap.parse_args()

    # Get all routes allowed to be originated by the ASN
    self_origin_routes = get_routes_for_asn(args.asn)

    # Get the routing policy for the ASN
    aut_num = list(linewise_whois(
        f"AS{args.asn}", args.aut_num_source_db or "whois.radb.net"))
    routing_policy = build_router_peer_data(args.asn, aut_num)
    
    # We need a list of router ids to iterate over
    router_ids = list(routing_policy.keys())
    
    # Ensure the output directory exists
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a template env
    templ_env = Environment(
        loader=PackageLoader("birdgen.conf"),
        autoescape=select_autoescape()
    )
    conf_template = templ_env.get_template("bird.conf.j2")
    
    # Generate a config for each router id
    for router_id in router_ids:
        file_contents = conf_template.render(
            own_asn=args.asn,
            router_id=router_id,
            self_origin_routes=self_origin_routes,
            routing_policy=routing_policy[router_id]
        )
        with open(output_dir / f"{router_id}.conf", "w") as f:
            for line in file_contents.splitlines():
                if not line.strip():
                   continue
                f.write(line + "\n")
        

    return 0


if __name__ == "__main__":
    sys.exit(main())
