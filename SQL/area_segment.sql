select a.rooms,
	   round(AVG(a.area_kitchen / a.area_total), 2) as avg_kitchen_rate,
	   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY round(a.area_kitchen / a.area_total, 2)) as median_kitchen_rate,
	   round(AVG(a.area_living / a.area_total), 2) as avg_living_rate,
	   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY round(a.area_living / a.area_total, 2)) as median_living_rate
from apartments a 
group by a.rooms
order by 1