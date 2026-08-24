with floor_segment as (
	select case
		when floor = floors_total then 'Last_floor'
		when floor = 1 then 'First_floor'
		else 'Mid_floor'
	end as category,
	price_month,
	area_total,
	round(price_month::numeric / area_total, 2) as price_m2
	from apartments
)
select category,
	   count(*) as count_offers,
	   round(avg(price_m2), 2) as price_m2_avg,
	   PERCENTILE_CONT(0.5) within group (order by price_m2) as price_m2_median,
	   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_month) as price_month_median
from floor_segment
group by category
order by price_m2_avg