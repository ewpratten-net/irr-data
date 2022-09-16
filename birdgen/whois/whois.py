import subprocess


def make_whois_query(query: str, server: str = "whois.radb.net") -> str:

    return subprocess.Popen(["whois", "-h", server, query], stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
