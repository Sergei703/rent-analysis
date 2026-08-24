select offer_id,
	   rooms,
	   price_month,
	   round(price_month / area_total, 2) as price_m2,
	   round(avg(price_month) over (partition by rooms), 2) as avg_price_rooms,
	   round(avg(price_month / area_total) over (partition by rooms), 2) as avg_price_m2,
	   round(((price_month / area_total)::numeric / avg(price_month / area_total) over (partition by rooms) - 1) * 100, 2) as price_m2_deviation,
	   round((price_month::numeric / avg(price_month) over (partition by rooms) - 1) * 100, 2) as price_month_deviation,
	   dense_rank() over(partition by rooms order by price_month desc) as price_rank
from apartments