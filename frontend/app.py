import streamlit as st
import pandas as pd
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="FleetVision 360",
    page_icon="🚚",
    layout="wide"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🚚 FleetVision 360")
st.subheader("Fleet Management & ETA Prediction Dashboard")

st.write(
    "Monitor orders, vehicles, revenue, fuel efficiency "
    "and predict delivery time using Machine Learning."
)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

st.sidebar.header("🔐 Database Connection")

password = st.sidebar.text_input(
    "PostgreSQL Password",
    type="password"
)


def get_database_connection():

    if not password:
        return None

    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username="postgres",
        password=password,
        host="localhost",
        port=5432,
        database="fleetvision"
    )

    return create_engine(database_url)


# --------------------------------------------------
# LOAD ORDER DATA
# --------------------------------------------------

@st.cache_data
def load_orders(_engine):

    query = """
        SELECT
            o.order_id,
            o.customer_id,
            o.route_id,
            o.vehicle_id,
            o.driver_id,
            o.order_date,
            o.delivery_date,
            o.status,
            o.order_amount,
            o.distance_km,
            v.vehicle_type AS vehicle_type,
            c.segment AS segment
        FROM public.orders AS o
        LEFT JOIN public.vehicles AS v
            ON o.vehicle_id = v.vehicle_id
        LEFT JOIN public.customers AS c
            ON o.customer_id = c.customer_id
    """

    return pd.read_sql(query, _engine)


# --------------------------------------------------
# LOAD FUEL DATA
# --------------------------------------------------

@st.cache_data
def load_fuel(_engine):

    query = "SELECT * FROM public.fuel_records"

    return pd.read_sql(query, _engine)


# --------------------------------------------------
# LOAD GPS DATA
# --------------------------------------------------

@st.cache_data
def load_gps(_engine):

    query = """
        SELECT
            gps_event_id,
            vehicle_id,
            timestamp,
            latitude,
            longitude,
            speed_kmph,
            fuel_level_percent
        FROM public.gps_events
    """

    return pd.read_sql(query, _engine)


# ==================================================
# DASHBOARD
# ==================================================

if password:

    try:

        # --------------------------------------------------
        # DATABASE CONNECTION
        # --------------------------------------------------

        engine = get_database_connection()

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        st.sidebar.success("Database Connected ✅")


        # --------------------------------------------------
        # LOAD DATA
        # --------------------------------------------------

        orders = load_orders(engine)

        fuel = load_fuel(engine)

        gps = load_gps(engine)


        # --------------------------------------------------
        # DASHBOARD FILTERS
        # --------------------------------------------------

        st.sidebar.header("🔎 Dashboard Filters")


        # --------------------------------------------------
        # ORDER STATUS FILTER
        # --------------------------------------------------

        status_options = ["All"] + sorted(
            orders["status"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_status = st.sidebar.selectbox(
            "Order Status",
            status_options,
            key="order_status_filter"
        )


        # --------------------------------------------------
        # VEHICLE TYPE FILTER
        # --------------------------------------------------

        vehicle_options = ["All"] + sorted(
            orders["vehicle_type"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_vehicle = st.sidebar.selectbox(
            "Vehicle Type",
            vehicle_options,
            key="vehicle_type_filter"
        )


        # --------------------------------------------------
        # CUSTOMER SEGMENT FILTER
        # --------------------------------------------------

        segment_options = ["All"] + sorted(
            orders["segment"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_segment = st.sidebar.selectbox(
            "Customer Segment",
            segment_options,
            key="customer_segment_filter"
        )


        # --------------------------------------------------
        # APPLY FILTERS
        # --------------------------------------------------

        filtered_orders = orders.copy()

        if selected_status != "All":

            filtered_orders = filtered_orders[
                filtered_orders["status"] == selected_status
            ]


        if selected_vehicle != "All":

            filtered_orders = filtered_orders[
                filtered_orders["vehicle_type"] == selected_vehicle
            ]


        if selected_segment != "All":

            filtered_orders = filtered_orders[
                filtered_orders["segment"] == selected_segment
            ]


        st.sidebar.write(
            f"Filtered Orders: {len(filtered_orders):,}"
        )


        # ==================================================
        # EXECUTIVE SUMMARY
        # ==================================================

        st.header("📊 Executive Summary")

        st.write(
            "High-level business overview of fleet operations, "
            "orders, revenue, fuel and vehicle performance."
        )


        # --------------------------------------------------
        # EXECUTIVE SUMMARY CALCULATIONS
        # --------------------------------------------------

        executive_total_orders = len(filtered_orders)

        executive_delivered = len(
            filtered_orders[
                filtered_orders["status"] == "Delivered"
            ]
        )

        executive_cancelled = len(
            filtered_orders[
                filtered_orders["status"] == "Cancelled"
            ]
        )

        executive_returned = len(
            filtered_orders[
                filtered_orders["status"] == "Returned"
            ]
        )


        executive_delivery_rate = (
            executive_delivered
            / executive_total_orders
            * 100
            if executive_total_orders > 0
            else 0
        )


        executive_revenue = (
            filtered_orders["order_amount"].sum()
        )


        executive_avg_order_value = (
            executive_revenue
            / executive_total_orders
            if executive_total_orders > 0
            else 0
        )


        executive_total_vehicles = (
            filtered_orders["vehicle_id"].nunique()
        )


        executive_total_fuel = (
            fuel["litres"].sum()
        )


        executive_total_fuel_cost = (
            fuel["fuel_cost"].sum()
        )


        # --------------------------------------------------
        # EXECUTIVE KPI ROW 1
        # --------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "📦 Total Orders",
            f"{executive_total_orders:,}"
        )

        col2.metric(
            "✅ Delivered",
            f"{executive_delivered:,}"
        )

        col3.metric(
            "🚚 Vehicles",
            f"{executive_total_vehicles:,}"
        )

        col4.metric(
            "💰 Revenue",
            f"₹{executive_revenue:,.0f}"
        )


        # --------------------------------------------------
        # EXECUTIVE KPI ROW 2
        # --------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "📈 Delivery Rate",
            f"{executive_delivery_rate:.2f}%"
        )

        col2.metric(
            "❌ Cancelled",
            f"{executive_cancelled:,}"
        )

        col3.metric(
            "↩️ Returned",
            f"{executive_returned:,}"
        )

        col4.metric(
            "💵 Avg Order Value",
            f"₹{executive_avg_order_value:,.2f}"
        )


        # --------------------------------------------------
        # EXECUTIVE KPI ROW 3
        # --------------------------------------------------

        col1, col2 = st.columns(2)

        col1.metric(
            "⛽ Total Fuel",
            f"{executive_total_fuel:,.2f} L"
        )

        col2.metric(
            "💸 Fuel Cost",
            f"₹{executive_total_fuel_cost:,.0f}"
        )


        # --------------------------------------------------
        # ORDER STATUS SUMMARY
        # --------------------------------------------------

        st.subheader("📦 Order Status Summary")

        executive_status_summary = (
            filtered_orders["status"]
            .value_counts()
        )

        st.bar_chart(
            executive_status_summary
        )


        # --------------------------------------------------
        # REVENUE BY VEHICLE TYPE
        # --------------------------------------------------

        st.subheader("🚚 Revenue by Vehicle Type")

        executive_revenue_vehicle = (
            filtered_orders
            .groupby("vehicle_type")["order_amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            executive_revenue_vehicle
        )


        # --------------------------------------------------
        # ORDERS BY CUSTOMER SEGMENT
        # --------------------------------------------------

        st.subheader("👥 Orders by Customer Segment")

        executive_segment_orders = (
            filtered_orders["segment"]
            .value_counts()
        )

        st.bar_chart(
            executive_segment_orders
        )


        # --------------------------------------------------
        # TOP VEHICLES BY REVENUE
        # --------------------------------------------------

        st.subheader("🏆 Top 10 Vehicles by Revenue")

        executive_vehicle_revenue = (
            filtered_orders
            .groupby("vehicle_id")["order_amount"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        st.bar_chart(
            executive_vehicle_revenue
        )


        # --------------------------------------------------
        # EXECUTIVE SUMMARY TABLE
        # --------------------------------------------------

        st.subheader("📋 Executive Summary Details")

        executive_summary_table = pd.DataFrame(
            {
                "Metric": [
                    "Total Orders",
                    "Delivered Orders",
                    "Cancelled Orders",
                    "Returned Orders",
                    "Delivery Rate",
                    "Revenue",
                    "Average Order Value",
                    "Vehicles",
                    "Total Fuel",
                    "Fuel Cost"
                ],
                "Value": [
                    f"{executive_total_orders:,}",
                    f"{executive_delivered:,}",
                    f"{executive_cancelled:,}",
                    f"{executive_returned:,}",
                    f"{executive_delivery_rate:.2f}%",
                    f"₹{executive_revenue:,.2f}",
                    f"₹{executive_avg_order_value:,.2f}",
                    f"{executive_total_vehicles:,}",
                    f"{executive_total_fuel:,.2f} L",
                    f"₹{executive_total_fuel_cost:,.2f}"
                ]
            }
        )

        st.dataframe(
            executive_summary_table,
            use_container_width=True,
            hide_index=True
        )


        # ==================================================
        # FLEET OVERVIEW
        # ==================================================

        total_orders = len(filtered_orders)

        delivered_orders = len(
            filtered_orders[
                filtered_orders["status"] == "Delivered"
            ]
        )

        cancelled_orders = len(
            filtered_orders[
                filtered_orders["status"] == "Cancelled"
            ]
        )

        returned_orders = len(
            filtered_orders[
                filtered_orders["status"] == "Returned"
            ]
        )

        delivery_rate = (
            delivered_orders / total_orders * 100
            if total_orders > 0
            else 0
        )

        total_revenue = filtered_orders["order_amount"].sum()

        avg_order_value = (
            filtered_orders["order_amount"].mean()
            if total_orders > 0
            else 0
        )


        st.header("📊 Fleet Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Orders",
            f"{total_orders:,}"
        )

        col2.metric(
            "Delivered Orders",
            f"{delivered_orders:,}"
        )

        col3.metric(
            "Delivery Rate",
            f"{delivery_rate:.2f}%"
        )

        col4.metric(
            "Total Revenue",
            f"₹{total_revenue:,.0f}"
        )


        col5, col6, col7 = st.columns(3)

        col5.metric(
            "Cancelled Orders",
            f"{cancelled_orders:,}"
        )

        col6.metric(
            "Returned Orders",
            f"{returned_orders:,}"
        )

        col7.metric(
            "Average Order Value",
            f"₹{avg_order_value:,.2f}"
        )


        # ==================================================
        # ORDER STATUS
        # ==================================================

        st.header("📦 Order Status")

        status_counts = (
            filtered_orders["status"]
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Orders")
        )

        col1, col2 = st.columns(2)

        with col1:

            st.dataframe(
                status_counts,
                use_container_width=True
            )

        with col2:

            st.bar_chart(
                status_counts.set_index("Status")
            )


        # ==================================================
        # ORDER STATUS DISTRIBUTION
        # ==================================================

        st.subheader("📦 Order Status Distribution")

        status_distribution = (
            filtered_orders["status"]
            .value_counts()
        )

        st.bar_chart(
            status_distribution
        )


        # ==================================================
        # DISTANCE ANALYSIS
        # ==================================================

        st.header("🛣️ Distance Analysis")

        st.line_chart(
            filtered_orders[
                ["distance_km"]
            ].head(500)
        )


        # ==================================================
        # REVENUE ANALYSIS
        # ==================================================

        st.header("💰 Revenue Analysis")

        revenue_by_status = (
            filtered_orders
            .groupby("status")["order_amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            revenue_by_status
        )


        # ==================================================
        # REVENUE BY ORDER STATUS
        # ==================================================

        st.subheader("💰 Revenue by Order Status")

        revenue_by_order_status = (
            filtered_orders
            .groupby("status")["order_amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            revenue_by_order_status
        )


        # ==================================================
        # AI ETA PREDICTION
        # ==================================================

        st.header("🤖 AI ETA Prediction")

        st.write(
            "Enter delivery information below to predict "
            "the expected delivery time."
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            distance_km = st.number_input(
                "Distance (km)",
                min_value=1.0,
                value=300.0
            )

            route_distance_km = st.number_input(
                "Route Distance (km)",
                min_value=1.0,
                value=300.0
            )

            estimated_time_minutes = st.number_input(
                "Estimated Time (minutes)",
                min_value=1.0,
                value=500.0
            )

            capacity_kg = st.number_input(
                "Vehicle Capacity (kg)",
                min_value=1.0,
                value=1000.0
            )


        with col2:

            age = st.number_input(
                "Driver Age",
                min_value=18,
                max_value=70,
                value=35
            )

            experience_years = st.number_input(
                "Driver Experience (years)",
                min_value=0.0,
                value=5.0
            )

            order_month = st.number_input(
                "Order Month",
                min_value=1,
                max_value=12,
                value=6
            )

            order_day_of_week = st.number_input(
                "Day of Week",
                min_value=0,
                max_value=6,
                value=2
            )


        with col3:

            is_weekend = st.selectbox(
                "Weekend?",
                [0, 1]
            )

            vehicle_type = st.selectbox(
                "Vehicle Type",
                [
                    "Truck",
                    "Van",
                    "Mini Truck"
                ]
            )

            manufacturer = st.selectbox(
                "Manufacturer",
                [
                    "Tata",
                    "Ashok Leyland",
                    "Mahindra"
                ]
            )

            fuel_type = st.selectbox(
                "Fuel Type",
                [
                    "Diesel",
                    "Petrol",
                    "CNG",
                    "Electric"
                ]
            )


        # --------------------------------------------------
        # PREDICTION BUTTON
        # --------------------------------------------------

        if st.button(
            "🚀 Predict Delivery Time",
            type="primary"
        ):

            payload = {
                "distance_km": distance_km,
                "route_distance_km": route_distance_km,
                "estimated_time_minutes": estimated_time_minutes,
                "capacity_kg": capacity_kg,
                "age": age,
                "experience_years": experience_years,
                "order_month": order_month,
                "order_day_of_week": order_day_of_week,
                "is_weekend": is_weekend,
                "vehicle_type": vehicle_type,
                "manufacturer": manufacturer,
                "fuel_type": fuel_type
            }

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/predict-eta",
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:

                    result = response.json()

                    predicted_days = result[
                        "predicted_delivery_days"
                    ]

                    st.success(
                        f"🚚 Predicted Delivery Time: "
                        f"{predicted_days} days"
                    )

                else:

                    st.error(
                        f"API Error: {response.status_code}"
                    )

            except requests.exceptions.RequestException:

                st.error(
                    "FastAPI is not running. "
                    "Start FastAPI using: "
                    "uvicorn api.main:app --reload"
                )


        # ==================================================
        # FUEL EFFICIENCY
        # ==================================================

        st.header("⛽ Fuel Efficiency")

        total_fuel = fuel["litres"].sum()

        total_fuel_cost = fuel["fuel_cost"].sum()


        vehicle_distance = (
            fuel
            .groupby("vehicle_id")["odometer_km"]
            .agg(["min", "max"])
        )

        vehicle_distance["distance_km"] = (
            vehicle_distance["max"]
            - vehicle_distance["min"]
        )

        total_distance = (
            vehicle_distance["distance_km"].sum()
        )


        fuel_efficiency = (
            total_distance / total_fuel
            if total_fuel > 0
            else 0
        )


        fuel_cost_per_km = (
            total_fuel_cost / total_distance
            if total_distance > 0
            else 0
        )


        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Fuel",
            f"{total_fuel:,.2f} L"
        )

        col2.metric(
            "Fuel Cost",
            f"₹{total_fuel_cost:,.0f}"
        )

        col3.metric(
            "Distance",
            f"{total_distance:,.0f} km"
        )

        col4.metric(
            "Fuel Efficiency",
            f"{fuel_efficiency:.2f} km/L"
        )


        st.metric(
            "Fuel Cost per KM",
            f"₹{fuel_cost_per_km:.2f}"
        )


        # --------------------------------------------------
        # FUEL BY VEHICLE
        # --------------------------------------------------

        st.subheader("🚚 Fuel Consumption by Vehicle")

        fuel_by_vehicle = (
            fuel
            .groupby("vehicle_id")["litres"]
            .sum()
            .sort_values(ascending=False)
            .head(20)
        )

        st.bar_chart(
            fuel_by_vehicle
        )


        # --------------------------------------------------
        # FUEL COST BY VEHICLE
        # --------------------------------------------------

        st.subheader("💰 Fuel Cost by Vehicle")

        cost_by_vehicle = (
            fuel
            .groupby("vehicle_id")["fuel_cost"]
            .sum()
            .sort_values(ascending=False)
            .head(20)
        )

        st.bar_chart(
            cost_by_vehicle
        )


        # ==================================================
        # MAINTENANCE DASHBOARD
        # ==================================================

        st.header("🔧 Maintenance Dashboard")

        maintenance_query = """
            SELECT
                maintenance_id,
                vehicle_id,
                maintenance_date,
                maintenance_type,
                cost,
                status
            FROM public.maintenance
        """

        maintenance = pd.read_sql(
            maintenance_query,
            engine
        )


        total_maintenance_records = len(
            maintenance
        )

        total_maintenance_cost = (
            maintenance["cost"].sum()
        )

        average_maintenance_cost = (
            maintenance["cost"].mean()
            if total_maintenance_records > 0
            else 0
        )

        vehicles_maintained = (
            maintenance["vehicle_id"].nunique()
        )


        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Maintenance Records",
            f"{total_maintenance_records:,}"
        )

        col2.metric(
            "Total Maintenance Cost",
            f"₹{total_maintenance_cost:,.0f}"
        )

        col3.metric(
            "Average Cost",
            f"₹{average_maintenance_cost:,.2f}"
        )

        col4.metric(
            "Vehicles Maintained",
            f"{vehicles_maintained:,}"
        )


        st.subheader("🛠️ Maintenance by Type")

        maintenance_by_type = (
            maintenance
            .groupby("maintenance_type")["cost"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            maintenance_by_type
        )


        st.subheader("🚚 Maintenance Cost by Vehicle")

        maintenance_by_vehicle = (
            maintenance
            .groupby("vehicle_id")["cost"]
            .sum()
            .sort_values(ascending=False)
            .head(20)
        )

        st.bar_chart(
            maintenance_by_vehicle
        )


        st.subheader("📊 Maintenance Status")

        maintenance_status = (
            maintenance["status"]
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Records")
        )

        st.dataframe(
            maintenance_status,
            use_container_width=True
        )


        st.subheader("📋 Maintenance Records")

        recent_maintenance = (
            maintenance
            .sort_values(
                "maintenance_date",
                ascending=False
            )
            .head(20)
        )

        st.dataframe(
            recent_maintenance,
            use_container_width=True
        )


        # ==================================================
        # DELIVERY PERFORMANCE
        # ==================================================

        st.header("📦 Delivery Performance")

        delivered = filtered_orders[
            filtered_orders["status"] == "Delivered"
        ].copy()

        total_delivered = len(delivered)


        if total_delivered > 0:

            delivered["order_date"] = pd.to_datetime(
                delivered["order_date"]
            )

            delivered["delivery_date"] = pd.to_datetime(
                delivered["delivery_date"]
            )

            delivered["delivery_days"] = (
                delivered["delivery_date"]
                - delivered["order_date"]
            ).dt.total_seconds() / (
                24 * 60 * 60
            )

            average_delivery_days = (
                delivered["delivery_days"].mean()
            )

            on_time = delivered[
                delivered["delivery_days"] <= 3
            ]

            late = delivered[
                delivered["delivery_days"] > 3
            ]

            on_time_orders = len(on_time)

            late_orders = len(late)

            on_time_rate = (
                on_time_orders
                / total_delivered
                * 100
            )

        else:

            average_delivery_days = 0

            on_time_orders = 0

            late_orders = 0

            on_time_rate = 0


        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Delivered Orders",
            f"{total_delivered:,}"
        )

        col2.metric(
            "On-Time Orders",
            f"{on_time_orders:,}"
        )

        col3.metric(
            "Late Orders",
            f"{late_orders:,}"
        )

        col4.metric(
            "On-Time Rate",
            f"{on_time_rate:.2f}%"
        )


        st.metric(
            "Average Delivery Time",
            f"{average_delivery_days:.2f} days"
        )


        st.subheader("⏱️ On-Time vs Late Deliveries")

        delivery_performance = pd.DataFrame(
            {
                "Type": [
                    "On-Time",
                    "Late"
                ],
                "Orders": [
                    on_time_orders,
                    late_orders
                ]
            }
        )


        col1, col2 = st.columns(2)

        with col1:

            st.dataframe(
                delivery_performance,
                use_container_width=True
            )

        with col2:

            st.bar_chart(
                delivery_performance.set_index("Type")
            )


        if total_delivered > 0:

            st.subheader("📅 Delivery Time Distribution")

            delivery_distribution = (
                delivered["delivery_days"]
                .round(0)
                .value_counts()
                .sort_index()
            )

            st.bar_chart(
                delivery_distribution
            )


            st.subheader("📈 Monthly Delivered Orders")

            delivered["month"] = (
                delivered["delivery_date"]
                .dt.to_period("M")
                .astype(str)
            )

            monthly_deliveries = (
                delivered
                .groupby("month")
                .size()
            )

            st.line_chart(
                monthly_deliveries
            )


        # ==================================================
        # CUSTOMER ANALYTICS
        # ==================================================

        st.header("👥 Customer Analytics")

        try:

            customer_df = pd.read_sql(
                """
                SELECT
                    customer_id,
                    customer_name,
                    segment,
                    city,
                    signup_date
                FROM public.customers
                """,
                engine
            )


            customer_orders = (
                filtered_orders
                .groupby("customer_id")
                .agg(
                    total_orders=("order_id", "count"),
                    total_spending=("order_amount", "sum"),
                    average_order_value=("order_amount", "mean")
                )
                .reset_index()
            )


            filtered_customer_ids = (
                filtered_orders["customer_id"].unique()
            )


            filtered_customers = customer_df[
                customer_df["customer_id"].isin(
                    filtered_customer_ids
                )
            ].copy()


            customer_analysis = filtered_customers.merge(
                customer_orders,
                on="customer_id",
                how="left"
            )


            customer_analysis[
                [
                    "total_orders",
                    "total_spending",
                    "average_order_value"
                ]
            ] = customer_analysis[
                [
                    "total_orders",
                    "total_spending",
                    "average_order_value"
                ]
            ].fillna(0)


            total_customers = len(
                customer_analysis
            )

            active_customers = (
                customer_analysis["total_orders"] > 0
            ).sum()

            total_customer_spending = (
                customer_analysis["total_spending"].sum()
            )

            avg_customer_spending = (
                customer_analysis["total_spending"].mean()
                if total_customers > 0
                else 0
            )


            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Total Customers",
                f"{total_customers:,}"
            )

            col2.metric(
                "Active Customers",
                f"{active_customers:,}"
            )

            col3.metric(
                "Total Spending",
                f"₹{total_customer_spending:,.0f}"
            )

            col4.metric(
                "Avg Customer Spending",
                f"₹{avg_customer_spending:,.0f}"
            )


            st.subheader("Customer Segments")

            segment_summary = (
                customer_analysis
                .groupby("segment")
                .agg(
                    customers=("customer_id", "count"),
                    spending=("total_spending", "sum")
                )
                .reset_index()
            )


            st.bar_chart(
                segment_summary.set_index("segment")[
                    "customers"
                ]
            )


            st.subheader(
                "Top 10 Customers by Spending"
            )

            top_customers = (
                customer_analysis
                .sort_values(
                    "total_spending",
                    ascending=False
                )
                .head(10)
            )


            st.dataframe(
                top_customers[
                    [
                        "customer_id",
                        "customer_name",
                        "segment",
                        "city",
                        "total_orders",
                        "total_spending",
                        "average_order_value"
                    ]
                ],
                use_container_width=True
            )


        except Exception as e:

            st.error(
                f"Customer Analytics Error: {e}"
            )


        # ==================================================
        # ROUTE & GPS ANALYTICS
        # ==================================================

        st.header("📍 Route & GPS Analytics")

        gps["timestamp"] = pd.to_datetime(
            gps["timestamp"],
            errors="coerce"
        )


        total_gps_events = len(gps)

        active_gps_vehicles = (
            gps["vehicle_id"].nunique()
        )

        average_speed = (
            gps["speed_kmph"].mean()
        )

        average_fuel_level = (
            gps["fuel_level_percent"].mean()
        )


        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "📍 Total GPS Events",
            f"{total_gps_events:,}"
        )

        col2.metric(
            "🚚 Active Vehicles",
            f"{active_gps_vehicles:,}"
        )

        col3.metric(
            "🛣️ Average Speed",
            f"{average_speed:.2f} km/h"
        )

        col4.metric(
            "⛽ Average Fuel Level",
            f"{average_fuel_level:.2f}%"
        )


        st.subheader("🚗 Average Speed by Vehicle")

        speed_by_vehicle = (
            gps
            .groupby("vehicle_id")["speed_kmph"]
            .mean()
            .sort_values(ascending=False)
            .head(20)
        )

        st.bar_chart(
            speed_by_vehicle
        )


        st.subheader("📈 GPS Events Over Time")

        gps_time = (
            gps.groupby(
                gps["timestamp"].dt.date
            )
            .size()
        )

        st.line_chart(
            gps_time
        )


        st.subheader("🗺️ GPS Vehicle Locations")

        gps_map_data = gps[
            [
                "latitude",
                "longitude"
            ]
        ].dropna().copy()

        gps_map_data = gps_map_data.rename(
            columns={
                "latitude": "lat",
                "longitude": "lon"
            }
        )

        gps_map_data = gps_map_data.head(5000)

        st.map(gps_map_data)


        st.subheader("🗺️ GPS Location Data")

        gps_location_data = gps[
            [
                "vehicle_id",
                "timestamp",
                "latitude",
                "longitude",
                "speed_kmph",
                "fuel_level_percent"
            ]
        ].copy()

        st.dataframe(
            gps_location_data.head(100),
            use_container_width=True
        )


        # ==================================================
        # ROUTE ANOMALY DETECTION
        # ==================================================

        st.header("🚨 Route Anomaly Detection")


        gps_anomaly = gps[
            [
                "gps_event_id",
                "vehicle_id",
                "speed_kmph",
                "fuel_level_percent"
            ]
        ].copy()


        gps_anomaly["speed_kmph"] = pd.to_numeric(
            gps_anomaly["speed_kmph"],
            errors="coerce"
        )

        gps_anomaly["fuel_level_percent"] = pd.to_numeric(
            gps_anomaly["fuel_level_percent"],
            errors="coerce"
        )


        gps_anomaly = gps_anomaly.dropna(
            subset=[
                "speed_kmph",
                "fuel_level_percent"
            ]
        )


        high_speed = (
            gps_anomaly["speed_kmph"] > 90
        )

        low_fuel = (
            gps_anomaly["fuel_level_percent"] < 10
        )

        critical_condition = (
            (gps_anomaly["speed_kmph"] > 100)
            &
            (gps_anomaly["fuel_level_percent"] < 15)
        )


        gps_anomaly["route_status"] = "Normal"


        gps_anomaly.loc[
            high_speed
            |
            low_fuel
            |
            critical_condition,
            "route_status"
        ] = "Anomaly"


        total_gps_events_anomaly = len(
            gps_anomaly
        )

        anomaly_count = (
            gps_anomaly["route_status"] == "Anomaly"
        ).sum()

        normal_count = (
            gps_anomaly["route_status"] == "Normal"
        ).sum()


        anomaly_rate = (
            anomaly_count
            / total_gps_events_anomaly
            * 100
            if total_gps_events_anomaly > 0
            else 0
        )


        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "📍 GPS Events",
            f"{total_gps_events_anomaly:,}"
        )

        col2.metric(
            "🚨 Anomalies",
            f"{anomaly_count:,}"
        )

        col3.metric(
            "✅ Normal Events",
            f"{normal_count:,}"
        )

        col4.metric(
            "📊 Anomaly Rate",
            f"{anomaly_rate:.2f}%"
        )


        st.subheader(
            "🚨 Normal vs Anomaly GPS Events"
        )

        anomaly_distribution = (
            gps_anomaly["route_status"]
            .value_counts()
        )

        st.bar_chart(
            anomaly_distribution
        )


        st.subheader(
            "🚚 Anomalies by Vehicle"
        )

        anomalies_by_vehicle = (
            gps_anomaly[
                gps_anomaly["route_status"] == "Anomaly"
            ]
            .groupby("vehicle_id")
            .size()
            .sort_values(
                ascending=False
            )
            .head(20)
        )

        st.bar_chart(
            anomalies_by_vehicle
        )


        st.subheader(
            "🔍 Detected Route Anomalies"
        )

        anomaly_data = gps_anomaly[
            gps_anomaly["route_status"] == "Anomaly"
        ]

        st.dataframe(
            anomaly_data.head(100),
            use_container_width=True
        )


        # ==================================================
        # FUEL ANOMALY DETECTION
        # ==================================================

        st.header("⛽ Fuel Anomaly Detection")


        fuel_anomaly = fuel[
            [
                "fuel_record_id",
                "vehicle_id",
                "fuel_date",
                "litres",
                "odometer_km",
                "fuel_cost"
            ]
        ].copy()


        fuel_anomaly["litres"] = pd.to_numeric(
            fuel_anomaly["litres"],
            errors="coerce"
        )

        fuel_anomaly["odometer_km"] = pd.to_numeric(
            fuel_anomaly["odometer_km"],
            errors="coerce"
        )

        fuel_anomaly["fuel_cost"] = pd.to_numeric(
            fuel_anomaly["fuel_cost"],
            errors="coerce"
        )


        fuel_anomaly = fuel_anomaly.dropna(
            subset=[
                "vehicle_id",
                "litres",
                "odometer_km",
                "fuel_cost"
            ]
        )


        fuel_summary = (
            fuel_anomaly
            .groupby("vehicle_id")
            .agg(
                total_litres=("litres", "sum"),
                total_fuel_cost=("fuel_cost", "sum"),
                minimum_odometer=("odometer_km", "min"),
                maximum_odometer=("odometer_km", "max"),
                fuel_records=("fuel_record_id", "count")
            )
            .reset_index()
        )


        fuel_summary["distance_km"] = (
            fuel_summary["maximum_odometer"]
            - fuel_summary["minimum_odometer"]
        )


        fuel_summary["fuel_efficiency_km_per_litre"] = (
            fuel_summary["distance_km"]
            / fuel_summary["total_litres"]
        )


        fuel_summary["fuel_cost_per_km"] = (
            fuel_summary["total_fuel_cost"]
            / fuel_summary["distance_km"]
        )


        fuel_summary = fuel_summary.replace(
            [float("inf"), float("-inf")],
            pd.NA
        )


        fuel_summary = fuel_summary.dropna(
            subset=[
                "fuel_efficiency_km_per_litre",
                "fuel_cost_per_km"
            ]
        )


        if len(fuel_summary) > 0:

            efficiency_threshold = (
                fuel_summary[
                    "fuel_efficiency_km_per_litre"
                ].quantile(0.10)
            )

            cost_threshold = (
                fuel_summary[
                    "fuel_cost_per_km"
                ].quantile(0.90)
            )

        else:

            efficiency_threshold = 0

            cost_threshold = 0


        fuel_summary["fuel_status"] = "Normal"


        if len(fuel_summary) > 0:

            fuel_summary.loc[
                (
                    fuel_summary[
                        "fuel_efficiency_km_per_litre"
                    ]
                    < efficiency_threshold
                )
                |
                (
                    fuel_summary[
                        "fuel_cost_per_km"
                    ]
                    > cost_threshold
                ),
                "fuel_status"
            ] = "Anomaly"


        total_fuel_vehicles = len(
            fuel_summary
        )

        fuel_anomaly_count = (
            fuel_summary["fuel_status"] == "Anomaly"
        ).sum()

        normal_fuel_vehicles = (
            fuel_summary["fuel_status"] == "Normal"
        ).sum()


        fuel_anomaly_rate = (
            fuel_anomaly_count
            / total_fuel_vehicles
            * 100
            if total_fuel_vehicles > 0
            else 0
        )


        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "🚚 Vehicles Analyzed",
            f"{total_fuel_vehicles:,}"
        )

        col2.metric(
            "🚨 Fuel Anomalies",
            f"{fuel_anomaly_count:,}"
        )

        col3.metric(
            "✅ Normal Vehicles",
            f"{normal_fuel_vehicles:,}"
        )

        col4.metric(
            "📊 Anomaly Rate",
            f"{fuel_anomaly_rate:.2f}%"
        )


        st.subheader(
            "⛽ Normal vs Anomaly Vehicles"
        )

        fuel_distribution = (
            fuel_summary["fuel_status"]
            .value_counts()
        )

        st.bar_chart(
            fuel_distribution
        )


        st.subheader(
            "🚚 Fuel Efficiency by Vehicle"
        )

        efficiency_by_vehicle = (
            fuel_summary
            .set_index("vehicle_id")[
                "fuel_efficiency_km_per_litre"
            ]
            .sort_values()
        )

        st.bar_chart(
            efficiency_by_vehicle
        )


        st.subheader(
            "🔍 Detected Fuel Anomalies"
        )

        fuel_anomalies = fuel_summary[
            fuel_summary["fuel_status"] == "Anomaly"
        ].copy()


        fuel_anomalies = fuel_anomalies.sort_values(
            "fuel_efficiency_km_per_litre"
        )


        st.dataframe(
            fuel_anomalies[
                [
                    "vehicle_id",
                    "total_litres",
                    "total_fuel_cost",
                    "distance_km",
                    "fuel_efficiency_km_per_litre",
                    "fuel_cost_per_km",
                    "fuel_records",
                    "fuel_status"
                ]
            ],
            use_container_width=True
        )


        # ==================================================
        # MAINTENANCE RISK PREDICTION
        # ==================================================

        st.header("🔧 Maintenance Risk Prediction")


        maintenance_risk_query = """
            SELECT
                maintenance_id,
                vehicle_id,
                maintenance_date,
                maintenance_type,
                cost,
                status
            FROM public.maintenance
        """


        maintenance_risk = pd.read_sql(
            maintenance_risk_query,
            engine
        )


        maintenance_risk["cost"] = pd.to_numeric(
            maintenance_risk["cost"],
            errors="coerce"
        )


        maintenance_risk["maintenance_date"] = pd.to_datetime(
            maintenance_risk["maintenance_date"],
            errors="coerce"
        )


        maintenance_risk = maintenance_risk.dropna(
            subset=[
                "vehicle_id",
                "cost",
                "maintenance_date"
            ]
        )


        maintenance_summary = (
            maintenance_risk
            .groupby("vehicle_id")
            .agg(
                maintenance_records=(
                    "maintenance_id",
                    "count"
                ),
                total_maintenance_cost=(
                    "cost",
                    "sum"
                ),
                average_maintenance_cost=(
                    "cost",
                    "mean"
                )
            )
            .reset_index()
        )


        if len(maintenance_summary) > 0:

            records_threshold = (
                maintenance_summary[
                    "maintenance_records"
                ].quantile(0.75)
            )

            cost_threshold = (
                maintenance_summary[
                    "total_maintenance_cost"
                ].quantile(0.75)
            )

        else:

            records_threshold = 0

            cost_threshold = 0


        maintenance_summary["risk_score"] = 0


        maintenance_summary.loc[
            maintenance_summary[
                "maintenance_records"
            ] >= records_threshold,
            "risk_score"
        ] += 1


        maintenance_summary.loc[
            maintenance_summary[
                "total_maintenance_cost"
            ] >= cost_threshold,
            "risk_score"
        ] += 1


        maintenance_summary["risk_level"] = "Low Risk"


        maintenance_summary.loc[
            maintenance_summary["risk_score"] == 1,
            "risk_level"
        ] = "Medium Risk"


        maintenance_summary.loc[
            maintenance_summary["risk_score"] >= 2,
            "risk_level"
        ] = "High Risk"


        total_maintenance_vehicles = len(
            maintenance_summary
        )


        high_risk_vehicles = (
            maintenance_summary["risk_level"]
            == "High Risk"
        ).sum()


        medium_risk_vehicles = (
            maintenance_summary["risk_level"]
            == "Medium Risk"
        ).sum()


        low_risk_vehicles = (
            maintenance_summary["risk_level"]
            == "Low Risk"
        ).sum()


        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "🚚 Vehicles Analyzed",
            f"{total_maintenance_vehicles:,}"
        )

        col2.metric(
            "🔴 High Risk",
            f"{high_risk_vehicles:,}"
        )

        col3.metric(
            "🟡 Medium Risk",
            f"{medium_risk_vehicles:,}"
        )

        col4.metric(
            "🟢 Low Risk",
            f"{low_risk_vehicles:,}"
        )


        st.subheader(
            "🔧 Maintenance Risk Distribution"
        )

        risk_distribution = (
            maintenance_summary["risk_level"]
            .value_counts()
        )

        st.bar_chart(
            risk_distribution
        )


        st.subheader(
            "📊 Maintenance Records by Vehicle"
        )

        maintenance_by_vehicle = (
            maintenance_summary
            .set_index("vehicle_id")[
                "maintenance_records"
            ]
            .sort_values(
                ascending=False
            )
            .head(20)
        )

        st.bar_chart(
            maintenance_by_vehicle
        )


        st.subheader(
            "🔴 High Risk Vehicles"
        )

        high_risk_data = (
            maintenance_summary[
                maintenance_summary["risk_level"]
                == "High Risk"
            ]
            .sort_values(
                "risk_score",
                ascending=False
            )
        )


        st.dataframe(
            high_risk_data[
                [
                    "vehicle_id",
                    "maintenance_records",
                    "total_maintenance_cost",
                    "average_maintenance_cost",
                    "risk_score",
                    "risk_level"
                ]
            ],
            use_container_width=True
        )


    # ==================================================
    # DATABASE ERROR
    # ==================================================

    except Exception as e:

        st.error(
            f"Database connection failed: {e}"
        )


# ==================================================
# PASSWORD NOT ENTERED
# ==================================================

else:

    st.info(
        "👈 Enter your PostgreSQL password "
        "in the sidebar to start the dashboard."
    )