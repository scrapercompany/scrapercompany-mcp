"""Nightly prices for one hotel across the coming weeks, then its cheapest and dearest nights.

    python rate_calendar.py "The Savoy" London --days 60 --currency GBP

Costs 10 credits: resolve_hotel (2) + hotel_rate_calendar (8), whatever the number of nights.
"""

import argparse

from scrapercompany_mcp import call

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("hotel", help="hotel name as a guest would type it")
parser.add_argument("city", help="city, so a brand name matches the right property")
parser.add_argument("--days", type=int, default=60, help="nights to price, up to 330 (default 60)")
parser.add_argument("--currency", default="USD")
args = parser.parse_args()

match = call("resolve_hotel", name=args.hotel, city=args.city, limit=1)["matches"][0]
calendar = call("hotel_rate_calendar", token=match["token"], days=args.days, currency=args.currency)

rates = sorted(calendar["rates"], key=lambda r: r["rate_total"])
print(f"{match['name']}: {len(rates)} of {args.days} nights priced, {args.currency}, 2 adults, 1 night each")
if calendar.get("unpriced_dates"):
    print(f"No price (sold out or not yet bookable): {len(calendar['unpriced_dates'])} nights")
print("\nCheapest nights")
for r in rates[:5]:
    print(f"  {r['stay_date']}  {r['rate_total']:>10,.2f}")
print("Dearest nights")
for r in rates[-5:][::-1]:
    print(f"  {r['stay_date']}  {r['rate_total']:>10,.2f}")
