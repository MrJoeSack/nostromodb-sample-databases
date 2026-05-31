#!/usr/bin/env python3
"""
Deterministic generator for the semantic-shores-json dataset.

Produces a small, JSON-native test corpus modeled on the SemanticShoresDB
SQL Server sample (real-estate listings). Vectors are intentionally omitted;
instead the records mix flat/columnar fields (the easy case for a JSON OLAP
column-store) with deliberate nesting, variable-length arrays, sparse fields,
and mixed-type fields, to exercise NostromoDB's "no cliff on nesting / mixed
types" claim.

Output is newline-delimited JSON (one object per line) under ./data/.
Run: python generate.py
Deterministic: fixed seed, stable ordering, no timestamps.
"""

import json
import random
from pathlib import Path

SEED = 1979  # Alien (1979); the Nostromo's year. Fixed for reproducibility.
N_PROPERTIES = 1000
N_AGENTS = 12

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
    "dock", "garden", "wine_cellar", "rooftop_deck",
]
STREET_NAMES = [
    "Tideline", "Beacon", "Saltwind", "Coral", "Harbor", "Marlin", "Dune",
    "Cypress", "Anchor", "Spindrift", "Lantern", "Cove", "Mariner", "Gull",
]
STREET_SUFFIX = ["St", "Ave", "Way", "Ct", "Dr", "Ln", "Blvd", "Terrace"]

FIRST = ["Ava", "Noah", "Mia", "Leo", "Zoe", "Kai", "Ivy", "Eli",
         "Nora", "Owen", "Lena", "Ravi"]
LAST = ["Okafor", "Nguyen", "Castellanos", "Bergstrom", "Haddad", "Park",
        "Delgado", "Volkov", "Mbeki", "Saito", "Romano", "Fischer"]
SPECIALTIES = ["waterfront", "luxury", "first_time_buyer", "investment",
               "land", "condo", "relocation", "historic"]

# Search-phrase corpus: (phrase, category) used in the SemanticShoresDB demos.
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


def make_agents(rng):
    agents = []
    for i in range(N_AGENTS):
        first, last = FIRST[i], LAST[i]
        agents.append({
            "agent_id": i + 1,
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}@semanticshores.example",
            "phone": f"+1-555-{rng.randint(100, 999)}-{rng.randint(1000, 9999)}",
            "rating": round(rng.uniform(3.6, 5.0), 1),
            "years_experience": rng.randint(1, 28),
            "specialties": rng.sample(SPECIALTIES, rng.randint(1, 3)),
        })
    return agents


def make_property(rng, pid):
    city, state = rng.choice(CITIES)
    ptype = rng.choices(
        PROPERTY_TYPES, weights=[45, 25, 15, 8, 7], k=1
    )[0]
    is_land = ptype == "Land"

    beds = 0 if is_land else rng.randint(1, 6)
    baths = 0 if is_land else round(rng.choice([1, 1.5, 2, 2.5, 3, 3.5, 4]), 1)
    sqft = 0 if is_land else rng.randint(650, 5200)
    lot = rng.randint(1500, 40000)
    year = rng.randint(1912, 2025)
    base = (sqft * rng.randint(280, 950)) if not is_land else lot * rng.randint(20, 120)
    price = int(round(base, -3)) + rng.randint(0, 50) * 1000

    # nested address + geo (natural sub-field access tests)
    street = f"{rng.randint(10, 9990)} {rng.choice(STREET_NAMES)} {rng.choice(STREET_SUFFIX)}"
    zip_code = f"9{rng.randint(1000, 8999)}"
    rec = {
        "id": pid,
        "property_type": ptype,
        "neighborhood": rng.choice(NEIGHBORHOODS),
        "address": {
            "street": street,
            "city": city,
            "state": state,
            "zip": zip_code,
        },
        "geo": {
            "lat": round(rng.uniform(32.5, 48.4), 5),
            "lng": round(rng.uniform(-124.4, -117.0), 5),
        },
        "bedrooms": beds,
        "bathrooms": baths,
        "sqft": sqft,
        "lot_size": lot,
        "year_built": year,
        "list_price": price,
        "listing_date": f"2026-{rng.randint(1, 5):02d}-{rng.randint(1, 28):02d}",
        "agent_id": rng.randint(1, N_AGENTS),
        # variable-length array of scalars (repeated field shredding)
        "features": rng.sample(FEATURES, rng.randint(0, 6)),
        # variable-length array of objects (nested repeated shredding)
        "price_history": [
            {
                "date": f"202{rng.randint(3, 5)}-{rng.randint(1, 12):02d}-15",
                "price": int(round(price * rng.uniform(0.82, 1.04), -3)),
            }
            for _ in range(rng.randint(1, 4))
        ],
    }

    # --- deliberate mixed-type / sparse fields (the "no cliff" stress) ---

    # hoa_fee: number | "none" | null | (absent)
    roll = rng.random()
    if roll < 0.45:
        rec["hoa_fee"] = rng.choice([0, 95, 150, 240, 320, 480, 600])
    elif roll < 0.65:
        rec["hoa_fee"] = "none"
    elif roll < 0.80:
        rec["hoa_fee"] = None
    # else: field omitted entirely (sparse column)

    # garage: int count | bool | string  (same field, three JSON types)
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

    if is_land:
        # land listings drop building fields entirely (irregular schema)
        for k in ("bedrooms", "bathrooms", "sqft"):
            rec.pop(k, None)

    return rec


def make_phrases(rng):
    rows = []
    for i, (phrase, cat) in enumerate(PHRASE_BANK):
        rows.append({
            "id": i + 1,
            "phrase": phrase,
            "category": cat,
            "token_count": len(phrase.split()),
        })
    return rows


def write_ndjson(path, rows):
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            f.write("\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)

    agents = make_agents(rng)
    properties = [make_property(rng, pid) for pid in range(1, N_PROPERTIES + 1)]
    phrases = make_phrases(rng)

    write_ndjson(OUT / "agents.json", agents)
    write_ndjson(OUT / "properties.json", properties)
    write_ndjson(OUT / "search_phrases.json", phrases)

    print(f"agents.json         {len(agents):>5} rows")
    print(f"properties.json     {len(properties):>5} rows")
    print(f"search_phrases.json {len(phrases):>5} rows")


if __name__ == "__main__":
    main()
