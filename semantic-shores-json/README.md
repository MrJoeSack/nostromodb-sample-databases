# semantic-shores-json

Synthetic real-estate listings as newline-delimited JSON. Loosely based on the
[SemanticShoresDB](https://github.com/MrJoeSack/sqlserver-sample-databases/tree/master/semantic-shores-db)
SQL Server sample, reshaped for JSON (no vectors).

## Files

| File | Rows |
| --- | --- |
| `data/properties.json` | 1,000 |
| `data/agents.json` | 12 |
| `data/search_phrases.json` | 40 |

## Shape

Records are mostly flat, with some nested objects (`address`, `geo`,
`price_history[].source`, agent `office`), variable-length arrays (`features`,
`price_history`), and a few fields that carry more than one JSON type across
records:

- `hoa_fee` — number, `"none"`, null, or absent
- `garage` — integer, boolean, or string
- `renovation_year` — integer, `"n/a"`, or null
- `owner` — string, object, or array
- `Land` listings omit `bedrooms` / `bathrooms` / `sqft` / `stories`

## Regenerate

```sh
python generate.py                      # default (1,000)
python generate.py --properties 100000  # larger
```

Deterministic for a given size and seed. No dependencies, no network.

`queries.sql` has example queries. Statements are single-line, and the NDJSON
files import with `{'NDJSON': true}`.
