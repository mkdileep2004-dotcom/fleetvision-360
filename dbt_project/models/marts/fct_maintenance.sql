WITH maintenance_summary AS (
    SELECT
        vehicle_id,
        COUNT(*) AS maintenance_count,
        SUM(cost) AS total_maintenance_cost,
        AVG(cost) AS average_maintenance_cost,
        MIN(maintenance_date) AS first_maintenance_date,
        MAX(maintenance_date) AS last_maintenance_date
    FROM {{ ref('stg_maintenance') }}
    GROUP BY vehicle_id
)

SELECT
    v.vehicle_id,
    v.registration_number,
    v.vehicle_type,
    v.manufacturer,
    v.fuel_type,
    v.status,

    COALESCE(m.maintenance_count, 0)
        AS maintenance_count,

    ROUND(
        COALESCE(m.total_maintenance_cost, 0)::numeric,
        2
    ) AS total_maintenance_cost,

    ROUND(
        COALESCE(m.average_maintenance_cost, 0)::numeric,
        2
    ) AS average_maintenance_cost,

    m.first_maintenance_date,
    m.last_maintenance_date

FROM {{ ref('stg_vehicles') }} v

LEFT JOIN maintenance_summary m
    ON v.vehicle_id = m.vehicle_id