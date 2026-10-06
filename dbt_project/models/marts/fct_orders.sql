SELECT
    o.order_id,
    o.order_date,
    o.delivery_date,
    o.status,
    o.order_amount,
    o.distance_km,

    c.customer_id,
    c.customer_name,
    c.segment,
    c.city,

    v.vehicle_id,
    v.registration_number,
    v.vehicle_type,
    v.fuel_type,

    d.driver_id,
    d.driver_name,
    d.experience_years,

    r.route_id,
    r.route_name,
    r.origin,
    r.destination,
    r.estimated_time_minutes,

    CASE
        WHEN o.delivery_date IS NOT NULL
        THEN o.delivery_date - o.order_date
        ELSE NULL
    END AS delivery_days

FROM {{ ref('stg_orders') }} o

LEFT JOIN {{ ref('stg_customers') }} c
    ON o.customer_id = c.customer_id

LEFT JOIN {{ ref('stg_vehicles') }} v
    ON o.vehicle_id = v.vehicle_id

LEFT JOIN {{ ref('stg_drivers') }} d
    ON o.driver_id = d.driver_id

LEFT JOIN {{ ref('stg_routes') }} r
    ON o.route_id = r.route_id