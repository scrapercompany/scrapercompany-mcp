"""Recent low-rated guest reviews for one hotel, and which ones still have no reply from the hotel.

    python review_watch.py "The Savoy" London --pages 3 --max-rating 3

Costs 2 credits for resolve_hotel plus 2 per page of 10 reviews. Pages that fail are free.
"""

import argparse

from scrapercompany_mcp import call

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("hotel")
parser.add_argument("city")
parser.add_argument("--pages", type=int, default=2, help="pages of 10 reviews (default 2)")
parser.add_argument("--max-rating", type=float, default=3, help="show reviews at or below this rating out of 5")
args = parser.parse_args()

match = call("resolve_hotel", name=args.hotel, city=args.city, limit=1)["matches"][0]
reviews = call("hotel_guest_reviews", property_token=match["token"], pages=args.pages)["reviews"]

def out_of_five(review: dict) -> float | None:
    if review.get("rating") is None:
        return None
    return review["rating"] * 5 / (review.get("rating_scale") or 5)

low = [r for r in reviews if (score := out_of_five(r)) is not None and score <= args.max_rating]
unreplied = [r for r in low if not r.get("management_reply")]
print(f"{match['name']}: {len(reviews)} recent reviews, {len(low)} at {args.max_rating}/5 or below, {len(unreplied)} without a reply")
for r in low:
    status = "replied" if r.get("management_reply") else "NO REPLY"
    text = " ".join((r.get("text") or "").replace("<br>", " ").split())[:160]
    print(f"\n  {out_of_five(r):.1f}/5  {r.get('date', '')}  {r.get('provider', '')}  [{status}]\n  {text}")
