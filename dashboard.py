import streamlit as st  # ✅ Streamlit import first
st.set_page_config(page_title="Satellite Anomalies Dashboard", layout="wide")  # ✅ First Streamlit command

import os
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import plotly.express as px
import urllib.parse  # Import for password encoding

# ✅ Load Database Credentials from Environment Variables (Render or Local)
db_config = {
    "host": os.getenv("MYSQLHOST", "127.0.0.1"),  # Default to localhost for local testing
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", "@nees115"),  
    "database": os.getenv("MYSQLDATABASE", "satellite_maintenance")
}

# ✅ Encode password to handle special characters
encoded_password = urllib.parse.quote_plus(db_config["password"])

# ✅ Create SQLAlchemy Engine with Port Support
try:
    engine = create_engine(f"mysql+pymysql://{db_config['user']}:{encoded_password}@{db_config['host']}/{db_config['database']}")
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

# ✅ Refresh Button Fix
if st.button("🔄 Refresh Data"):
    st.experimental_rerun()  # Use st.experimental_rerun() for Streamlit <1.19
