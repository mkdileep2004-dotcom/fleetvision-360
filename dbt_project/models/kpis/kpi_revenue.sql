WITH revenue_summary AS (
    SELECT
        COUNT(*) AS total_orders,

        SUM(order_amount) AS total_revenue,

        SUM(order_amount)
            FILTER (WHERE status = 'Delivered')
            AS delivered_revenue,

        SUM(order_amount)
            FILTER (WHERE status = 'Cancelled')
            AS cancelled_revenue,

        SUM(order_amount)
            FILTER (WHERE status = 'Returned')
            AS returned_revenue,

        AVG(order_amount) AS average_order_value,

        MAX(order_amount) AS maximum_order_value,

        MIN(order_amount) AS minimum_order_value

    FROM {{ ref('stg_orders') }}
)

SELECT
    total_orders,

    ROUND(
        COALESCE(total_revenue, 0)::numeric,
        2
    ) AS total_revenue,

    ROUND(
        COALESCE(delivered_revenue, 0)::numeric,
        2
    ) AS delivered_revenue,

    ROUND(
        COALESCE(cancelled_revenue, 0)::numeric,
        2
    ) AS cancelled_revenue,

    ROUND(
        COALESCE(returned_revenue, 0)::numeric,
        2
    ) AS returned_revenue,

    ROUND(
        COALESCE(average_order_value, 0)::numeric,
        2
    ) AS average_order_value,

    ROUND(
        COALESCE(maximum_order_value, 0)::numeric,
        2
    ) AS maximum_order_value,

    ROUND(
        COALESCE(minimum_order_value, 0)::numeric,
        2
    ) AS minimum_order_value

FROM revenue_summary