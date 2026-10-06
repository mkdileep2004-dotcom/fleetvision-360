WITH delivery_data AS (
    SELECT
        o.order_id,
        o.order_date,
        o.delivery_date,
        o.status,
        r.estimated_time_minutes,

        CASE
            WHEN o.delivery_date IS NOT NULL
                 AND o.status = 'Delivered'
            THEN
                EXTRACT(
                    EPOCH FROM (
                        o.delivery_date::timestamp
                        - o.order_date::timestamp
                    )
                ) / 3600
            ELSE NULL
        END AS actual_delivery_hours

    FROM {{ ref('stg_orders') }} o

    LEFT JOIN {{ ref('stg_routes') }} r
        ON o.route_id = r.route_id
),

classified AS (
    SELECT
        *,
        estimated_time_minutes / 60.0 AS estimated_delivery_hours,

        CASE
            WHEN status = 'Delivered'
                 AND actual_delivery_hours
                     <= estimated_time_minutes / 60.0
            THEN 1
            ELSE 0
        END AS on_time_flag

    FROM delivery_data
)

SELECT
    COUNT(*) FILTER (
        WHERE status = 'Delivered'
    ) AS delivered_orders,

    SUM(on_time_flag) AS on_time_orders,

    COUNT(*) FILTER (
        WHERE status = 'Delivered'
    ) - SUM(on_time_flag) AS late_orders,

    ROUND(
        (
            SUM(on_time_flag)::numeric
            /
            NULLIF(
                COUNT(*) FILTER (
                    WHERE status = 'Delivered'
                ),
                0
            )
        ) * 100,
        2
    ) AS on_time_delivery_rate_percent,

    ROUND(
        AVG(actual_delivery_hours)
        FILTER (
            WHERE status = 'Delivered'
        )::numeric,
        2
    ) AS average_actual_delivery_hours

FROM classified