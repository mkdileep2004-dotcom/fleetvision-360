WITH customer_summary AS (
    SELECT
        customer_id,
        COUNT(*) AS total_orders,
        COUNT(*) FILTER (WHERE status = 'Delivered') AS delivered_orders,
        COUNT(*) FILTER (WHERE status = 'Cancelled') AS cancelled_orders,
        COUNT(*) FILTER (WHERE status = 'Returned') AS returned_orders,
        SUM(order_amount) AS total_spending,
        SUM(order_amount) FILTER (WHERE status = 'Delivered') AS delivered_spending,
        AVG(order_amount) AS average_order_value
    FROM {{ ref('stg_orders') }}
    GROUP BY customer_id
)

SELECT
    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE cs.total_orders > 0
    ) AS customers_with_orders,

    COALESCE(SUM(cs.total_orders), 0) AS total_orders,

    COALESCE(SUM(cs.delivered_orders), 0) AS delivered_orders,

    COALESCE(SUM(cs.cancelled_orders), 0) AS cancelled_orders,

    COALESCE(SUM(cs.returned_orders), 0) AS returned_orders,

    ROUND(
        COALESCE(SUM(cs.total_spending), 0)::numeric,
        2
    ) AS total_customer_spending,

    ROUND(
        COALESCE(SUM(cs.delivered_spending), 0)::numeric,
        2
    ) AS delivered_customer_spending,

    ROUND(
        COALESCE(AVG(cs.average_order_value), 0)::numeric,
        2
    ) AS average_order_value

FROM {{ ref('stg_customers') }} c
LEFT JOIN customer_summary cs
    ON c.customer_id = cs.customer_id