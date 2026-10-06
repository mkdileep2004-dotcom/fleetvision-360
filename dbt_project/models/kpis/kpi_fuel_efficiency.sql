WITH fuel_summary AS (
    SELECT
        SUM(total_fuel_litres) AS total_fuel_litres,
        SUM(total_fuel_cost) AS total_fuel_cost,
        SUM(distance_km) AS total_distance_km
    FROM {{ ref('fct_fuel_efficiency') }}
)

SELECT
    ROUND(
        total_fuel_litres::numeric,
        2
    ) AS total_fuel_litres,

    ROUND(
        total_fuel_cost::numeric,
        2
    ) AS total_fuel_cost,

    ROUND(
        total_distance_km::numeric,
        2
    ) AS total_distance_km,

    CASE
        WHEN total_fuel_litres > 0
        THEN ROUND(
            (total_distance_km / total_fuel_litres)::numeric,
            2
        )
        ELSE 0
    END AS fleet_fuel_efficiency_km_per_litre,

    CASE
        WHEN total_distance_km > 0
        THEN ROUND(
            (total_fuel_cost / total_distance_km)::numeric,
            2
        )
        ELSE 0
    END AS fuel_cost_per_km

FROM fuel_summary