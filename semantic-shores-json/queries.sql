-- Example queries. Untested against NostromoDB; syntax is a guess and likely
-- needs adjustment. Tables assumed loaded as: properties, agents, phrases.

select count(*) from properties;

select property_type, count(*), avg(list_price)
from properties
group by property_type;

select address.city, count(*), avg(list_price), avg(days_on_market)
from properties
group by address.city;

select id, address.city, address.state, list_price
from properties
where address.state = 'CA'
limit 10;

select id, geo.lat, geo.lng
from properties
where geo.lat > 40 and geo.lng < -122;

select count(distinct neighborhood) from properties;

select id, price_history.0.price, price_history.0.source.channel
from properties
limit 10;

select hoa_fee, count(*) from properties group by hoa_fee;

select garage, count(*) from properties group by garage;

select property_type, count(*)
from properties
where sqft is null
group by property_type;

select a.last_name, count(*), avg(p.list_price)
from properties p
join agents a on p.agent_id = a.agent_id
group by a.last_name;

select id, address.city, list_price
from properties
order by list_price desc
limit 20;
