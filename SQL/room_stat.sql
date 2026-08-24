select rooms,
	   count(*) as offers_count,
	   count(*)::numeric / SUM(COUNT(*)) OVER () as offers_share,
	   PERCENTILE_CONT(0.5) within group (order by a.price_month) as price_median,
	   PERCENTILE_CONT(0.5) within group (order by a.area_total) as area_median
from apartments a 
group by rooms
order by rooms