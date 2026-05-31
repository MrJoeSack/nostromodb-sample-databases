-- Sample NostromoDB queries for the semantic-shores-json dataset.
--
-- NostromoDB is an in-process JSON OLAP column-store with a SQL-like front end
-- and "natural" nested sub-field access (dotted paths, no Postgres JSON syntax).
--
-- NOTE: these queries are written against NostromoDB's documented syntax and
-- have not been run end to end yet. Treat them as a starting battery, not a
-- verified test suite. Adjust function/keyword spellings to match the build.
--
-- Load (one-shot form):
--   nostromodb --db_path=/data/catalog.json --c "import from '/data/properties.json' into properties; ..."
-- Or interactively:
--   > import from '/data/properties.json' into properties;
--   > import from '/data/agents.json' into agents;
--   > import from '/data/search_phrases.json' into phrases;

-- 1. Sanity: row count (columnar path, should be the easy case).
select count(*) from properties;

-- 2. Flat aggregation / group-by on a low-cardinality column (dictionary-friendly).
select property_type, count(*), avg(list_price)
from properties
group by property_type;

-- 3. Natural nested sub-field access (address is a nested object).
select id, address.city, address.state, list_price
from properties
where address.state = 'CA'
limit 10;

-- 4. Group-by on a nested sub-field.
select address.city, count(*), avg(list_price)
from properties
group by address.city;

-- 5. Nested numeric sub-fields (geo bounding box).
select id, geo.lat, geo.lng
from properties
where geo.lat > 40 and geo.lng < -122;

-- 6. Variable-length array of scalars (features). Tests repeated-field shredding.
--    Membership / unnest spelling will depend on NostromoDB's array syntax.
select id, features
from properties
where features.0 is not null
limit 10;

-- 7. Array of objects (price_history). Tests nested repeated shredding.
select id, price_history.0.price, list_price
from properties
limit 10;

-- 8. Mixed-type column stress: hoa_fee is number | "none" | null | absent.
--    The point is that NostromoDB should not fall off a cliff here.
select hoa_fee, count(*)
from properties
group by hoa_fee;

-- 9. Mixed-type column stress: garage is int | bool | string in the same field.
select garage, count(*)
from properties
group by garage;

-- 10. Sparse / irregular schema: Land listings omit bedrooms/bathrooms/sqft.
select property_type, count(*)
from properties
where sqft is null
group by property_type;

-- 11. Join properties to agents on agent_id (binary contains a hash-join path).
select a.first_name, a.last_name, count(*) as listings, avg(p.list_price)
from properties p
join agents a on p.agent_id = a.agent_id
group by a.first_name, a.last_name;

-- 12. Top-N (sort + limit).
select id, address.city, list_price
from properties
order by list_price desc
limit 20;
