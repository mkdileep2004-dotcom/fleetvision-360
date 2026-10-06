WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        COUNT(*) FILTER (
            WHERE status = 'Delivered'
        ) AS delivered_order_count,
        COUNT(*) FILTER (
            WHERE status = 'Cancelled'
        ) AS cancelled_order_count,
        COUNT(*) FILTER (
            WHERE status = 'Returned'
        ) AS returned_order_count,
        SUM(order_amount) AS total_spending,
        SUM(order_amount) FILTER (
            WHERE status = 'Delivered'
        ) AS delivered_spending,
        AVG(order_amount) AS average_order_value
    FROM {{ ref('stg_orders') }}
    GROUP BY customer_id
)

SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    c.city,
    c.signup_date,

    COALESCE(o.order_count, 0) AS order_count,
    COALESCE(o.delivered_order_count, 0) AS delivered_order_count,
    COALESCE(o.cancelled_order_count, 0) AS cancelled_order_count,
    COALESCE(o.returned_order_count, 0) AS returned_order_count,

    ROUND(
        COALESCE(o.total_spending, 0)::numeric,
        2
    ) AS total_spending,

    ROUND(
        COALESCE(o.delivered_spending, 0)::numeric,
        2
    ) AS delivered_spending,

    ROUND(
        COALESCE(o.average_order_value, 0)::numeric,
        2
    ) AS average_order_value

FROM {{ ref('stg_customers') }} c

LEFT JOIN customer_orders o
    ON c.customer_id = o.customer_id