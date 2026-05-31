#!/usr/bin/env python3
"""Synthetic JSON sample data (real-estate listings).

Deterministic (fixed seed). Size is configurable.
Output is newline-delimited JSON under ./data/.

  python generate.py                      # default size
  python generate.py --properties 100000  # larger
"""

import argparse
import json
import random
from pathlib import Path

SEED = 1979
DEFAULT_PROPERTIES = 1000
DEFAULT_AGENTS = 12

OUT = Path(__file__).parent / "data"

CITIES = [
    ("Marin Bay", "CA"), ("Coral Heights", "CA"), ("Pelagic Point", "CA"),
    ("Tidewater", "OR"), ("Saltmarsh", "OR"), ("Harborview", "WA"),
    ("Cape Mira", "WA"), ("Dunesend", "CA"),
]
NEIGHBORHOODS = [
    "Old Harbor", "Lighthouse Row", "Kelp Flats", "Mariner's Bluff",
    "Driftwood", "Saltaire", "Cormorant Cove", "Anchorage Hill",
    "Foggy Hollow", "Pier District", "Seaglass", "North Jetty",
]
PROPERTY_TYPES = ["SingleFamily", "Condo", "Townhouse", "MultiFamily", "Land"]
FEATURES = [
    "pool", "garage", "solar", "ocean_view", "fireplace", "hardwood",
    "renovated_kitchen", "smart_home", "ev_charger", "guest_house",
    "dock", "garden", "wine_cellar", "rooftop_deck", "gym", "elevator",
]
STREET_NAMES = [
    "Tideline", "Beacon", "Saltwind", "Coral", "Harbor", "Marlin", "Dune",
    "Cypress", "Anchor", "Spindrift", "Lantern", "Cove", "Mariner", "Gull",
]
STREET_SUFFIX = ["St", "Ave", "Way", "Ct", "Dr", "Ln", "Blvd", "Terrace"]
CHANNELS = ["mls", "agent", "auction", "relocation", "off_market"]

FIRST = ["Ava", "Noah", "Mia", "Leo", "Zoe", "Kai", "Ivy", "Eli",
         "Nora", "Owen", "Lena", "Ravi", "Sana", "Theo", "Imani", "Dario"]
LAST = ["Okafor", "Nguyen", "Castellanos", "Bergstrom", "Haddad", "Park",
        "Delgado", "Volkov", "Mbeki", "Saito", "Romano", "Fischer"]
SPECIALTIES = ["waterfront", "luxury", "first_time_buyer", "investment",
               "land", "condo", "relocation", "historic"]

PHRASE_BANK = [
    ("modern condo with ocean views", "lifestyle"),
    ("quiet family home near good schools", "family"),
    ("fixer-upper with investment potential", "investment"),
    ("walkable downtown loft", "lifestyle"),
    ("waterfront property with a private dock", "waterfront"),
    ("energy efficient home with solar panels", "sustainability"),
    ("spacious house with a big backyard", "family"),
    ("low maintenance townhouse for retirees", "lifestyle"),
    ("historic home with original details", "character"),
    ("new construction with smart home features", "tech"),
    ("affordable starter home under budget", "budget"),
    ("luxury estate with pool and guest house", "luxury"),
    ("pet friendly rental near the beach", "lifestyle"),
    ("multi family property for rental income", "investment"),
    ("vacant land with ocean view", "land"),
    ("move in ready single family home", "family"),
    ("open floor plan with natural light", "design"),
    ("home office with high speed internet", "remote_work"),
    ("garage with ev charging", "tech"),
    ("home near public transit", "commute"),
    ("renovated kitchen with island", "design"),
    ("gated community with security", "lifestyle"),
    ("home with a rooftop deck", "design"),
    ("cozy cottage close to the water", "character"),
    ("large lot for building a custom home", "land"),
    ("condo with low hoa fees", "budget"),
    ("house with a wine cellar", "luxury"),
    ("beachfront with sunset views", "waterfront"),
    ("fixer in an up and coming neighborhood", "investment"),
    ("accessible single story home", "accessibility"),
    ("home with a separate guest suite", "family"),
    ("property with mature gardens", "design"),
    ("modern minimalist new build", "design"),
    ("home with a boat slip", "waterfront"),
    ("turnkey vacation rental", "investment"),
    ("home with mountain and ocean views", "lifestyle"),
    ("close to hiking trails and parks", "outdoor"),
    ("duplex with strong rental history", "investment"),
    ("entry level condo for first time buyers", "budget"),
    ("estate home with ocean frontage", "luxury"),
]


def make_agents(rng, n):
    agents = []
    for i in range(n):
        first = FIRST[i % len(FIRST)]
        last = LAST[i % len(LAST)]
        city, region = rng.choice(CITIES)
        agents.append({
            "agent_id": i + 1,
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}{i}@semanticshores.example",
            "phone": f"+1-555-{rng.randint(100, 999)}-{rng.randint(1000, 9999)}",
            "rating": round(rng.uniform(3.6, 5.0), 1),
            "years_experience": rng.randint(1, 28),
            "specialties": rng.sample(SPECIALTIES, rng.randint(1, 3)),
            "office": {"city": city, "region": region},
        })
    return agents


def make_property(rng, pid, n_agents):
    city, state = rng.choice(CITIES)
    ptype = rng.choices(PROPERTY_TYPES, weights=[45, 25, 15, 8, 7], k=1)[0]
    is_land = ptype == "Land"

    beds = 0 if is_land else rng.randint(1, 6)
    baths = 0 if is_land else rng.choice([1, 1.5, 2, 2.5, 3, 3.5, 4])
    sqft = 0 if is_land else rng.randint(650, 5200)
    lot = rng.randint(1500, 40000)
    year = rng.randint(1912, 2025)
    base = (sqft * rng.randint(280, 950)) if not is_land else lot * rng.randint(20, 120)
    price = int(round(base, -3)) + rng.randint(0, 50) * 1000

    street = f"{rng.randint(10, 9990)} {rng.choice(STREET_NAMES)} {rng.choice(STREET_SUFFIX)}"
    zip_code = f"9{rng.randint(1000, 8999)}"

    rec = {
        "id": pid,
        "property_type": ptype,
        "neighborhood": rng.choice(NEIGHBORHOODS),
        "address": {
            "street": street, "city": city, "state": state, "zip": zip_code,
        },
        "geo": {
            "lat": round(rng.uniform(32.5, 48.4), 5),
            "lng": round(rng.uniform(-124.4, -117.0), 5),
        },
        "bedrooms": beds,
        "bathrooms": baths,
        "sqft": sqft,
        "lot_size": lot,
        "stories": rng.randint(1, 3),
        "parking_spaces": rng.randint(0, 4),
        "year_built": year,
        "list_price": price,
        "tax_assessed_value": int(round(price * rng.uniform(0.6, 0.95), -3)),
        "days_on_market": rng.randint(0, 240),
        "walk_score": rng.randint(10, 99),
        "school_rating": round(rng.uniform(1, 10), 1),
        "listing_date": f"2026-{rng.randint(1, 5):02d}-{rng.randint(1, 28):02d}",
        "agent_id": rng.randint(1, n_agents),
        "features": rng.sample(FEATURES, rng.randint(0, 8)),
        "price_history": [
            {
                "date": f"202{rng.randint(3, 5)}-{rng.randint(1, 12):02d}-15",
                "price": int(round(price * rng.uniform(0.82, 1.04), -3)),
                "source": {
                    "channel": rng.choice(CHANNELS),
                    "agent_id": rng.randint(1, n_agents),
                },
            }
            for _ in range(rng.randint(1, 4))
        ],
    }

    if not is_land and sqft:
        rec["price_per_sqft"] = round(price / sqft, 2)

    # hoa_fee: number | "none" | null | absent
    roll = rng.random()
    if roll < 0.45:
        rec["hoa_fee"] = rng.choice([0, 95, 150, 240, 320, 480, 600])
    elif roll < 0.65:
        rec["hoa_fee"] = "none"
    elif roll < 0.80:
        rec["hoa_fee"] = None

    # garage: int | bool | string
    g = rng.random()
    if g < 0.5:
        rec["garage"] = rng.randint(0, 3)
    elif g < 0.7:
        rec["garage"] = False
    elif g < 0.85:
        rec["garage"] = "carport"
    else:
        rec["garage"] = "detached"

    # renovation_year: int | "n/a" | null
    r = rng.random()
    if r < 0.4:
        rec["renovation_year"] = rng.randint(year, 2025)
    elif r < 0.7:
        rec["renovation_year"] = "n/a"
    else:
        rec["renovation_year"] = None

    # owner: string | object | array (same path, different container type)
    o = rng.random()
    if o < 0.55:
        rec["owner"] = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    elif o < 0.82:
        rec["owner"] = {
            "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
            "llc": rng.random() < 0.5,
        }
    else:
        rec["owner"] = [f"{rng.choice(FIRST)} {rng.choice(LAST)}"
                        for _ in range(rng.randint(2, 3))]

    if is_land:
        for k in ("bedrooms", "bathrooms", "sqft", "stories"):
            rec.pop(k, None)

    return rec


def make_phrases(rng):
    return [
        {"id": i + 1, "phrase": phrase, "category": cat,
         "token_count": len(phrase.split())}
        for i, (phrase, cat) in enumerate(PHRASE_BANK)
    ]


def write_ndjson(path, rows):
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            f.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--properties", type=int, default=DEFAULT_PROPERTIES)
    ap.add_argument("--agents", type=int, default=DEFAULT_AGENTS)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    agents = make_agents(rng, args.agents)
    properties = [make_property(rng, pid, args.agents)
                  for pid in range(1, args.properties + 1)]
    phrases = make_phrases(rng)

    write_ndjson(OUT / "agents.json", agents)
    write_ndjson(OUT / "properties.json", properties)
    write_ndjson(OUT / "search_phrases.json", phrases)

    print(f"agents.json         {len(agents):>7} rows")
    print(f"properties.json     {len(properties):>7} rows")
    print(f"search_phrases.json {len(phrases):>7} rows")


if __name__ == "__main__":
    main()
