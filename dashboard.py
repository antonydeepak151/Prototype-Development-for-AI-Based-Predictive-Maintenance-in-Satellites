import streamlit as st  # ✅ Streamlit import first
st.set_page_config(page_title="Satellite Anomalies Dashboard", layout="wide")  # ✅ First Streamlit command

import pandas as pd
import pymysql
from sqlalchemy import create_engine
import plotly.express as px

# ✅ Local MySQL Database Configuration
db_config = {
    "host": "127.0.0.1",  # ✅ Localhost for local MySQL
    "user": "root",  # ✅ Your local MySQL user
    "password": "%40nees115",  # ✅ Replace with your actual MySQL password
    "database": "satellite_maintenance",  # ✅ Your local database name
    "port": 3306,  # ✅ Default MySQL port
}

# ✅ Create SQLAlchemy Engine
engine = None  # Start as None, connect when needed

def connect_db():
    """Creates and returns a database engine."""
    global engine
    try:
        db_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        engine = create_engine(db_url, pool_pre_ping=True)
        st.success("✅ Connected to local MySQL database!")
    except Exception as e:
        st.error(f"🚨 Database Connection Error: {str(e)}")
        engine = None

# ✅ Connect to MySQL before fetching data
connect_db()

def fetch_anomalies():
    """Fetch latest anomalies from the database"""
    if engine is None:
        st.error("⚠️ No database connection available.")
        return pd.DataFrame()

    try:
        with engine.connect() as connection:
            query = "SELECT * FROM satellite_anomalies ORDER BY timestamp DESC LIMIT 100"
            df = pd.read_sql(query, con=connection)  
        return df
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        return pd.DataFrame()

# ✅ Streamlit Dashboard UI
st.title("🚀 Satellite Anomalies Dashboard")
st.write("Monitor detected anomalies in satellite systems.")

# ✅ Fetch Data
df = fetch_anomalies()

# ✅ Display Data
if not df.empty:
    st.subheader("🔍 Anomaly Data")
    st.dataframe(df)

    # ✅ Ensure timestamp is in datetime format
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # ✅ Line Chart - Trends over Time
        st.subheader("📊 Anomaly Trends Over Time")
        fig = px.line(df, x="timestamp", y="cpu_load", title="CPU Load Over Time", markers=True)
        st.plotly_chart(fig)

    # ✅ Bar Chart - Anomalies by System Status
    st.subheader("⚠️ Anomalies by System Status")
    fig = px.bar(df, x="system_status", title="Anomalies by System Status", color="system_status")
    st.plotly_chart(fig)

else:
    st.warning("⚠️ No anomalies detected yet.")

# ✅ Refresh Button for Live Data Updates
if st.button("🔄 Refresh Data"):
    st.experimental_rerun()  # ✅ Refresh Streamlit when clicked
