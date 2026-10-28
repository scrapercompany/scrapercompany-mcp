"""Rate parity for one hotel and one night: every booking site's price against the hotel's own site.

    python rate_parity.py "The Savoy" London --check-in 2026-11-20 --currency GBP --market GB

Costs 12 credits: resolve_hotel (2) + hotel_offers (10). Prices include taxes where the market shows them.
"""

import argparse
import datetime

from scrapercompany_mcp import call

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("hotel")
parser.add_argument("city")
parser.add_argument("--check-in", default=(datetime.date.today() + datetime.timedelta(days=14)).isoformat())
parser.add_argument("--currency", default="USD")
parser.add_argument("--market", help="country the guest searches from, e.g. US or GB")
args = parser.parse_args()

match = call("resolve_hotel", name=args.hotel, city=args.city, limit=1)["matches"][0]
extra = {"market": args.market} if args.market else {}
stay = call("hotel_offers", token=match["token"], check_in=args.check_in, currency=args.currency, **extra)

# Lowest price per seller (a seller can list several rooms).
best: dict[str, float] = {}
for offer in stay["offers"]:
    price = offer.get("price_per_night")
    if price is not None:
        best[offer["source"]] = min(price, best.get(offer["source"], price))

print(f"{match['name']}, {args.check_in}, 1 night, 2 adults, {stay.get('currency') or args.currency}")
if not best:
    print("No prices for that night (sold out, or not sold in this market). Try another date or --market.")
    raise SystemExit
direct = best.get("Official site")
for source, price in sorted(best.items(), key=lambda kv: kv[1]):
    note = ""
    if direct and source != "Official site":
        gap = (price - direct) / direct * 100
        note = f"{gap:+6.1f}% vs direct" + ("  <- undercuts the hotel" if gap < -1 else "")
    print(f"  {source:<24} {price:>10,.2f}  {note}")
if direct is None:
    print("The hotel's own site was not among the sellers for this night.")
