# FleetVision 360 - Schema Design

## Tables

1. vehicles - PK: vehicle_id
2. drivers - PK: driver_id
3. customers - PK: customer_id
4. routes - PK: route_id
5. orders - PK: order_id
6. gps_events - PK: gps_event_id
7. fuel_records - PK: fuel_record_id
8. maintenance - PK: maintenance_id
9. delivery_scans - PK: scan_id

## Foreign Keys

orders.customer_id -> customers.customer_id
orders.route_id -> routes.route_id
orders.vehicle_id -> vehicles.vehicle_id
orders.driver_id -> drivers.driver_id
gps_events.vehicle_id -> vehicles.vehicle_id
fuel_records.vehicle_id -> vehicles.vehicle_id
maintenance.vehicle_id -> vehicles.vehicle_id
delivery_scans.order_id -> orders.order_id

