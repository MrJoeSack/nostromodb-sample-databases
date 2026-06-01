-- Example queries. Each statement must be on a single line.
-- Data is newline-delimited JSON, so import with has_top_level_array=false.
-- Adjust the import paths to your local checkout.

import from 'data/agents.json' into agents options {'has_top_level_array': false};
import from 'data/properties.json' into properties options {'has_top_level_array': false};
import from 'data/search_phrases.json' into search_phrases options {'has_top_level_array': false};

select count(*) from properties;
select property_type, count(*), avg(list_price) from properties group by property_type;
select address.city, count(*), avg(list_price), avg(days_on_market) from properties group by address.city;
select id, address.city, address.state, list_price from properties where address.state = 'CA' limit 10;
select id, geo.lat, geo.lng from properties where geo.lat > 40 and geo.lng < -122;
select count(distinct neighborhood) from properties;
select id, features[0], price_history[0] from properties limit 10;
select hoa_fee, count(*) from properties group by hoa_fee;
select garage, count(*) from properties group by garage;
select property_type, count(*) from properties where sqft is null group by property_type;
select a::last_name, count(*), avg(p::list_price) from properties as p, agents as a where p::agent_id = a::agent_id group by a::last_name;
select id, address.city, list_price from properties order by list_price desc limit 20;
