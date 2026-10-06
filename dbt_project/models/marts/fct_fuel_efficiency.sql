WITH fuel_data AS (
    SELECT
        vehicle_id,
        COUNT(*) AS fuel_records,
        SUM(litres) AS total_fuel_litres,
        SUM(fuel_cost) AS total_fuel_cost,
        MIN(odometer_km) AS starting_odometer_km,
        MAX(odometer_km) AS ending_odometer_km
    FROM {{ ref('stg_fuel_records') }}
    GROUP BY vehicle_id
)

SELECT
    v.vehicle_id,
    v.registration_number,
    v.vehicle_type,
    v.manufacturer,
    v.fuel_type,

    COALESCE(f.fuel_records, 0) AS fuel_records,

    ROUND(
        COALESCE(f.total_fuel_litres, 0)::numeric,
        2
    ) AS total_fuel_litres,

    ROUND(
        COALESCE(f.total_fuel_cost, 0)::numeric,
        2
    ) AS total_fuel_cost,

    COALESCE(f.starting_odometer_km, 0)
        AS starting_odometer_km,

    COALESCE(f.ending_odometer_km, 0)
        AS ending_odometer_km,

    COALESCE(
        f.ending_odometer_km - f.starting_odometer_km,
        0
    ) AS distance_km,

    CASE
        WHEN COALESCE(f.total_fuel_litres, 0) > 0
        THEN ROUND(
            (
                f.ending_odometer_km
                - f.starting_odometer_km
            )::numeric
            / f.total_fuel_litres,
            2
        )
        ELSE 0
    END AS fuel_efficiency_km_per_litre,

    CASE
        WHEN COALESCE(
            f.ending_odometer_km - f.starting_odometer_km,
            0
        ) > 0
        THEN ROUND(
            f.total_fuel_cost::numeric
            /
            (
                f.ending_odometer_km
                - f.starting_odometer_km
            ),
            2
        )
        ELSE 0
    END AS fuel_cost_per_km

FROM {{ ref('stg_vehicles') }} v

LEFT JOIN fuel_data f
    ON v.vehicle_id = f.vehicle_id