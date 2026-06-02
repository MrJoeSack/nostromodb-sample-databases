-- Example queries. Each statement must be on a single line.
-- Import newline-delimited JSON with {'NDJSON': true}.
-- Adjust the import paths to your local checkout.

import from 'data/agents.json' into agents options {'NDJSON': true};
import from 'data/properties.json' into properties options {'NDJSON': true};
import from 'data/search_phrases.json' into search_phrases options {'NDJSON': true};

-- Concrete per-column types are derived after `pragma table_flush('properties');`
-- (the in-memory buffer reports JSON). Run that separately if you want typed columns.

select count(*) from properties;
select property_type, count(*), avg(list_price) from properties group by property_type;
select address.city, count(*), avg(list_price), avg(days_on_market) from properties group by address.city;
select id, address.city, address.state, list_price from properties where address.state = 'CA' limit 10;
select id, geo.lat, geo.lng from properties where geo.lat > 40 and geo.lng < -122;
select count(distinct neighborhood) from properties;
select id, features[0], price_history[0]{'price'} from properties limit 10;
select hoa_fee, count(*) from properties group by hoa_fee;
select garage, count(*) from properties group by garage;
select property_type, count(*) from properties where sqft is null group by property_type;
select a::last_name, count(*), avg(p::list_price) from properties as p, agents as a where p::agent_id = a::agent_id group by a::last_name;
select id, address.city, list_price from properties order by list_price desc limit 20;
