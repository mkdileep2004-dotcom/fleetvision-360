WITH gps_summary AS (
    SELECT
        vehicle_id,
        COUNT(*) AS gps_event_count,
        AVG(speed_kmph) AS avg_speed_kmph,
        MAX(speed_kmph) AS max_speed_kmph,
        AVG(fuel_level_percent) AS avg_fuel_level_percent
    FROM {{ ref('stg_gps_events') }}
    GROUP BY vehicle_id
),

fuel_summary AS (
    SELECT
        vehicle_id,
        COUNT(*) AS fuel_record_count,
        SUM(litres) AS total_fuel_litres,
        SUM(fuel_cost) AS total_fuel_cost,
        MAX(odometer_km) - MIN(odometer_km) AS odometer_distance_km
    FROM {{ ref('stg_fuel_records') }}
    GROUP BY vehicle_id
),

maintenance_summary AS (
    SELECT
        vehicle_id,
        COUNT(*) AS maintenance_count,
        SUM(cost) AS total_maintenance_cost
    FROM {{ ref('stg_maintenance') }}
    GROUP BY vehicle_id
)

SELECT
    v.vehicle_id,
    v.registration_number,
    v.vehicle_type,
    v.manufacturer,
    v.fuel_type,
    v.capacity_kg,
    v.status,

    COALESCE(g.gps_event_count, 0) AS gps_event_count,
    ROUND(COALESCE(g.avg_speed_kmph, 0)::numeric, 2) AS avg_speed_kmph,
    ROUND(COALESCE(g.max_speed_kmph, 0)::numeric, 2) AS max_speed_kmph,
    ROUND(COALESCE(g.avg_fuel_level_percent, 0)::numeric, 2)
        AS avg_fuel_level_percent,

    COALESCE(f.fuel_record_count, 0) AS fuel_record_count,
    ROUND(COALESCE(f.total_fuel_litres, 0)::numeric, 2)
        AS total_fuel_litres,
    ROUND(COALESCE(f.total_fuel_cost, 0)::numeric, 2)
        AS total_fuel_cost,
    COALESCE(f.odometer_distance_km, 0) AS odometer_distance_km,

    COALESCE(m.maintenance_count, 0) AS maintenance_count,
    ROUND(COALESCE(m.total_maintenance_cost, 0)::numeric, 2)
        AS total_maintenance_cost,

    CASE
        WHEN COALESCE(f.total_fuel_litres, 0) > 0
        THEN ROUND(
            COALESCE(f.odometer_distance_km, 0)::numeric
            / f.total_fuel_litres,
            2
        )
        ELSE 0
    END AS fuel_efficiency_km_per_litre

FROM {{ ref('stg_vehicles') }} v

LEFT JOIN gps_summary g
    ON v.vehicle_id = g.vehicle_id

LEFT JOIN fuel_summary f
    ON v.vehicle_id = f.vehicle_id

LEFT JOIN maintenance_summary m
    ON v.vehicle_id = m.vehicle_id