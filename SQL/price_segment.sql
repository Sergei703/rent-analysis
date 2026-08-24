with price_metr as (
	select price_month/area_total as price_m2,
		   area_total,
		   price_month
	from apartments
),
segmented as (
	select NTILE(4) over(order by price_m2) as tile,
	price_m2,
	area_total,
	price_month
	from price_metr
)
select case
		when tile = 1 then 'Economy'
		when tile = 2 then 'Standard'
		when tile = 3 then 'Comfort'
		else 'Premium'
		end as tile,
	   count(tile) as count_offers,
	   round(avg(price_month), 2) as avg_price_month,
	   round(avg(area_total), 2) as avg_area,
	   round(avg(price_m2), 2) as avg_price_m2
from segmented
group by tile
order by tile