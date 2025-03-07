import streamlit as st
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import plotly.express as px
import urllib.parse  # Import for password encoding
import os  # Import for environment variables

# Load database configuration from environment variables
db_config = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),  # Use environment variable
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "%40nees115)"),  # Keep empty for local dev
    "database": os.getenv("DB_NAME", "satellite_maintenance"),
    "port": int(os.getenv("DB_PORT", 3306))  # Default MySQL port
}

# Encode password to handle special characters
encoded_password = urllib.parse.quote_plus(db_config["password"])

# Create SQLAlchemy Engine
try:
    engine = create_engine(
        f"mysql+pymysql://{db_config['user']}:{encoded_password}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    st.success("✅ Successfully connected to the database!")
except Exception as e:
    st.error(f"🚨 Database Connection Error: {str(e)}")

def fetch_anomalies():
    """Fetch latest anomalies from the database"""
    try:
        with engine.connect() as connection:
            query = "SELECT * FROM satellite_anomalies ORDER BY timestamp DESC LIMIT 100"
            df = pd.read_sql(query, con=connection)  
        return df
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        return pd.DataFrame()

# Streamlit App Configuration
st.set_page_config(page_title="Satellite Anomalies Dashboard", layout="wide")

st.title("🚀 Satellite Anomalies Dashboard")
st.write("Monitor detected anomalies in satellite systems.")

# Fetch Data
df = fetch_anomalies()

# Display Data
if not df.empty:
    st.subheader("🔍 Anomaly Data")
    st.dataframe(df)

    # Ensure timestamp is in datetime format
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Line Chart - Trends over Time
        st.subheader("📊 Anomaly Trends Over Time")
        fig = px.line(df, x="timestamp", y="cpu_load", title="CPU Load Over Time", markers=True)
        st.plotly_chart(fig)

    # Bar Chart - Anomalies by System Status
    st.subheader("⚠️ Anomalies by System Status")
    fig = px.bar(df, x="system_status", title="Anomalies by System Status", color="system_status")
    st.plotly_chart(fig)
else:
    st.warning("⚠️ No anomalies detected yet.")

# Add Refresh Button
if st.button("🔄 Refresh Data"):
    st.rerun()
