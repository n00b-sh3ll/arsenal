#!/usr/bin/env python3
import os
import sys
import ipaddress
import requests

ABUSEIPDB_KEY='xxxxxxxx0bbfb25c87b0aa504f555fbca12fe6d3c69c3257017666680664d0d2803dd216745a5677f80'

ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/check"
THRESHOLD = 20   # somente acima ou igual a 20

def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def abuseipdb_score(ip: str, api_key: str, max_age_days: int = 90) -> int | None:
    headers = {"Accept": "application/json", "Key": api_key}
    params = {"ipAddress": ip, "maxAgeInDays": str(max_age_days)}
    r = requests.get(ABUSEIPDB_URL, headers=headers, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("data", {}).get("abuseConfidenceScore")

def main():
    filename = "list-ips.txt"

    api_key = os.getenv("ABUSEIPDB_KEY")
    if not api_key:
        print("ERRO: export ABUSEIPDB_KEY='SUA_CHAVE'", file=sys.stderr)
        sys.exit(2)

    try:
        with open(filename, "r") as f:
            ips = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    except FileNotFoundError:
        print("Arquivo list-ips.txt não encontrado", file=sys.stderr)
        sys.exit(2)

    for ip in ips:
        if not is_valid_ip(ip):
            continue

        try:
            score = abuseipdb_score(ip, api_key)

            # 🔥 somente imprime se >= 20
            if score is not None and score >= THRESHOLD:
                print(f"{ip}\tscore={score}")

        except Exception:
            continue

if __name__ == "__main__":
    main()
