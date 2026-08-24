with t1 as (
	select case
		when building_year <= 1960 then 'Historical'
		when 1960 < building_year and building_year < 1991 then 'Soviet'
		when 1990 < building_year and building_year < 2016 then 'Post-Soviet'
		else 'Modern'
	end as category,
	price_month,
	area_total 
	from apartments
)
select category,
	   count(*) as count_offers,
	   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY round(price_month / area_total, 2)) as median_price_m2,
	   round(avg(price_month / area_total), 2) as avg_price_m2,
	   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY area_total) as median_area
from t1
group by category