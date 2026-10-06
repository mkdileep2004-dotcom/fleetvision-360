WITH maintenance_summary AS (
    SELECT
        SUM(maintenance_count) AS total_maintenance_records,
        SUM(total_maintenance_cost) AS total_maintenance_cost,
        AVG(total_maintenance_cost) AS avg_maintenance_cost_per_vehicle
    FROM {{ ref('fct_maintenance') }}
)

SELECT
    total_maintenance_records,

    ROUND(
        total_maintenance_cost::numeric,
        2
    ) AS total_maintenance_cost,

    ROUND(
        avg_maintenance_cost_per_vehicle::numeric,
        2
    ) AS avg_maintenance_cost_per_vehicle

FROM maintenance_summary