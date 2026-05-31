# semantic-shores-json

A small, JSON-native real-estate dataset for testing [NostromoDB](https://nostromodb.io/).

It is a port of the **SemanticShoresDB** SQL Server 2025 vector-search sample
([source](https://github.com/MrJoeSack/sqlserver-sample-databases/tree/master/semantic-shores-db)),
reshaped for a JSON OLAP column-store. The vector embeddings are intentionally
removed. In their place the records carry nested objects, variable-length
arrays, sparse fields, and mixed-type fields, so the dataset doubles as a
stress test for NostromoDB's "no cliff on nesting / mixed types" design goal.

## Contents

| File | Format | Rows | Notes |
| --- | --- | --- | --- |
| `data/properties.json` | NDJSON | 1,000 | Listings. The main table. |
| `data/agents.json` | NDJSON | 12 | Listing agents (join target). |
| `data/search_phrases.json` | NDJSON | 40 | Natural-language search phrases from the SemanticShoresDB demos. |

All files are newline-delimited JSON (one object per line), UTF-8, keys sorted
for stable diffs.

## What each shape is testing

The data is **mostly flat and regular** on purpose. That is the case a JSON
column-store should shred into clean per-field streams and scan fastest. Layered
on top:

- **Nested objects** (`address.{street,city,state,zip}`, `geo.{lat,lng}`) test
  natural dotted sub-field access and group-by on nested fields.
- **Array of scalars** (`features`, 0-6 entries) tests repeated-field shredding.
- **Array of objects** (`price_history`, 1-4 `{date, price}` entries) tests
  nested repeated shredding.
- **Mixed-type fields** are the deliberate stressor:
  - `hoa_fee` is a number, the string `"none"`, `null`, or absent entirely.
  - `garage` is an integer count, a boolean, or a string (`"carport"` /
    `"detached"`) — three JSON types in one field.
  - `renovation_year` is an integer, the string `"n/a"`, or `null`.
- **Sparse / irregular schema**: the ~7% of listings with
  `property_type == "Land"` omit `bedrooms`, `bathrooms`, and `sqft` entirely.

### properties.json fields

`id`, `property_type`, `neighborhood`, `address{street,city,state,zip}`,
`geo{lat,lng}`, `bedrooms`, `bathrooms`, `sqft`, `lot_size`, `year_built`,
`list_price`, `listing_date`, `agent_id`, `features[]`,
`price_history[{date,price}]`, `hoa_fee`, `garage`, `renovation_year`.

## Loading into NostromoDB

One-shot:

```sh
nostromodb --db_path=/data/catalog.json --c \
  "import from '/data/properties.json' into properties; \
   import from '/data/agents.json' into agents; \
   import from '/data/search_phrases.json' into phrases; \
   select count(*) from properties;"
```

Interactive:

```
> import from '/data/properties.json' into properties;
> select address.city, count(*) from properties group by address.city;
```

See [`queries.sql`](./queries.sql) for a starter battery covering counts,
group-by, nested access, array access, the mixed-type columns, the sparse-schema
case, and a join to `agents`.

## Status

The sample queries reflect NostromoDB's documented syntax and haven't been run
end to end yet. Spellings of array/unnest and aggregate functions may need
adjustment to match the build.

## Regenerating

The data is produced deterministically (fixed seed) by `generate.py`:

```sh
python generate.py
```

No external dependencies, no network, no timestamps. Same seed reproduces the
same files byte for byte.
