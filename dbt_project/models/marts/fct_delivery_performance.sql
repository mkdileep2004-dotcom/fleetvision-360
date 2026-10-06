WITH order_metrics AS (
    SELECT
        order_id,
        order_date,
        delivery_date,
        status,
        order_amount,
        distance_km,

        CASE
            WHEN delivery_date IS NOT NULL
            THEN delivery_date - order_date
            ELSE NULL
        END AS delivery_days

    FROM {{ ref('stg_orders') }}
)

SELECT
    COUNT(*) AS total_orders,

    COUNT(*) FILTER (
        WHERE status = 'Delivered'
    ) AS delivered_orders,

    COUNT(*) FILTER (
        WHERE status = 'Cancelled'
    ) AS cancelled_orders,

    COUNT(*) FILTER (
        WHERE status = 'Returned'
    ) AS returned_orders,

    ROUND(
        (
            COUNT(*) FILTER (
                WHERE status = 'Delivered'
            )::numeric
            / NULLIF(COUNT(*), 0)
        ) * 100,
        2
    ) AS delivery_rate_percent,

    ROUND(
        AVG(delivery_days) FILTER (
            WHERE status = 'Delivered'
        )::numeric,
        2
    ) AS avg_delivery_days,

    ROUND(
        SUM(order_amount)::numeric,
        2
    ) AS total_order_value,

    ROUND(
        SUM(order_amount) FILTER (
            WHERE status = 'Delivered'
        )::numeric,
        2
    ) AS delivered_order_value,

    ROUND(
        AVG(distance_km)::numeric,
        2
    ) AS avg_delivery_distance_km

FROM order_metrics