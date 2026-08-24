with t1 as(
	select case
		when floor = 1 then 'First_floor'
		when floor = floors_total then 'Last_floor'
		else 'Mid_floor'
		end as category,
		PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_month / area_total) as price_m2_median
	from apartments
	group by category
),
t2 as (
	select category, price_m2_median
	from t1 
	where category = 'Mid_floor'
)
select t1.category,
	   ROUND(
    ((
        t1.price_m2_median /
        (SELECT t2.price_m2_median FROM t2) - 1
    ) * 100)::numeric,
    2
) as price_m2_change
from t1