select count(*) as count_offers,
	   PERCENTILE_CONT(0.5) WITHIN group (ORDER BY price_month) as median_price,
	   round(AVG(price_month/area_total), 2) as avg_m2,
	   ROUND(COUNT(*) FILTER (WHERE deposit = 0)::NUMERIC / COUNT(*), 2) AS deposit_0_rate
from apartments