"""Confirm SEC EDGAR access for a ticker.

Usage:
    python scripts/check_edgar.py AAPL

Reads SEC_USER_AGENT from the environment or a .env file in the repo root.
The SEC asks every client to identify itself with a name and email.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

REVENUE_TAGS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
]


def load_user_agent() -> str:
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("SEC_USER_AGENT="):
                os.environ.setdefault("SEC_USER_AGENT", line.split("=", 1)[1].strip().strip('"'))
    agent = os.environ.get("SEC_USER_AGENT", "")
    if "@" not in agent:
        sys.exit("Set SEC_USER_AGENT in .env, for example: SEC_USER_AGENT=\"Your Name you@psu.edu\"")
    return agent


def get_json(url: str, agent: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": agent, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/check_edgar.py TICKER")
    ticker = sys.argv[1].upper()
    agent = load_user_agent()

    tickers = get_json(TICKERS_URL, agent)
    match = next((row for row in tickers.values() if row["ticker"] == ticker), None)
    if match is None:
        sys.exit(f"{ticker} not found in the SEC ticker list.")
    cik = str(match["cik_str"]).zfill(10)
    print(f"{match['title']} ({ticker}) CIK {cik}")

    recent = get_json(SUBMISSIONS_URL.format(cik=cik), agent)["filings"]["recent"]
    for form in ("10-K", "10-Q"):
        if form in recent["form"]:
            i = recent["form"].index(form)
            print(f"Latest {form}: filed {recent['filingDate'][i]}, period {recent['reportDate'][i]}, accession {recent['accessionNumber'][i]}")

    facts = get_json(FACTS_URL.format(cik=cik), agent)["facts"].get("us-gaap", {})
    for tag in REVENUE_TAGS:
        annual = [f for f in facts.get(tag, {}).get("units", {}).get("USD", []) if f.get("form") == "10-K" and f.get("fp") == "FY"]
        if annual:
            latest = max(annual, key=lambda f: f["end"])
            print(f"Revenue ({tag}), fiscal year ending {latest['end']}: ${latest['val']:,}")
            break
    else:
        print("Revenue: none of the mapped tags found (check the tag mapping).")


if __name__ == "__main__":
    main()
