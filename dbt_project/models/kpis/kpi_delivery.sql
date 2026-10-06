SELECT
    total_orders,
    delivered_orders,
    cancelled_orders,
    returned_orders,
    delivery_rate_percent,
    avg_delivery_days,
    total_order_value,
    delivered_order_value,
    avg_delivery_distance_km
FROM {{ ref('fct_delivery_performance') }}