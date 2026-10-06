WITH vehicle_orders AS (
    SELECT
        vehicle_id,
        COUNT(*) AS order_count,
        COUNT(DISTINCT order_date) AS active_days
    FROM {{ ref('stg_orders') }}
    GROUP BY vehicle_id
),

vehicle_summary AS (
    SELECT
        v.vehicle_id,
        v.status,
        COALESCE(vo.order_count, 0) AS order_count,
        COALESCE(vo.active_days, 0) AS active_days
    FROM {{ ref('stg_vehicles') }} v
    LEFT JOIN vehicle_orders vo
        ON v.vehicle_id = vo.vehicle_id
)

SELECT
    COUNT(*) AS total_vehicles,

    COUNT(*) FILTER (
        WHERE status = 'Active'
    ) AS active_vehicles,

    COUNT(*) FILTER (
        WHERE status <> 'Active'
    ) AS inactive_vehicles,

    COUNT(*) FILTER (
        WHERE order_count > 0
    ) AS vehicles_used_for_orders,

    ROUND(
        (
            COUNT(*) FILTER (
                WHERE order_count > 0
            )::numeric
            / NULLIF(COUNT(*), 0)
        ) * 100,
        2
    ) AS vehicle_utilization_percent,

    SUM(order_count) AS total_vehicle_orders,

    ROUND(
        AVG(order_count)::numeric,
        2
    ) AS avg_orders_per_vehicle

FROM vehicle_summary