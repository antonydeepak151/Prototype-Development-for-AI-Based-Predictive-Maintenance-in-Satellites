import os
from fastapi import FastAPI
import joblib
import pymysql
import pandas as pd
from pydantic import BaseModel
import uvicorn

# ✅ Load the trained model
model = joblib.load("random_forest_satellite.pkl")

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ MySQL Database Connection (Updated for Railway)
db_config = {
    "host": os.getenv("MYSQLHOST", "caboose.proxy.rlwy.net"),  # ✅ Updated to Railway's host
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", "Anto115"),  # ✅ Corrected password
    "database": os.getenv("MYSQLDATABASE", "satellite_maintenance"),
    "port": int(os.getenv("MYSQLPORT", 3306)),  # ✅ Updated Railway's MySQL port (not 3306)
}

# ✅ Define Input Schema
class SensorData(BaseModel):
    cpu_load: float
    battery_charge: float
    radiation_exposure: float
    temperature_interior: float
    temperature_battery: float
    communication_signal_strength: float
    system_status: float
    voltage: float
    power: float
    external_temperature: float

# ✅ Root Endpoint
@app.get("/")
def home():
    return {"message": "Satellite Maintenance Prediction API is running!"}

# ✅ Database Connection Test Endpoint
@app.get("/test_db")
def test_db():
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT 1")  # ✅ Test query
        cursor.close()
        connection.close()
        return {"message": "✅ Database connection successful"}
    except Exception as e:
        return {"error": f"🚨 Database connection failed: {str(e)}"}

# ✅ Prediction Endpoint with Anomaly Storage
@app.post("/predict")
def predict(data: SensorData):
    try:
        # Convert input data to DataFrame
        input_df = pd.DataFrame([data.dict()])

        # Predict Anomaly
        prediction = model.predict(input_df)[0]

        # If anomaly detected, store it in the database
        if prediction == 1:
            try:
                connection = pymysql.connect(**db_config)
                cursor = connection.cursor()

                query = """
                INSERT INTO satellite_anomalies 
                (cpu_load, battery_charge, radiation_exposure, temperature_interior, temperature_battery, 
                communication_signal_strength, system_status, voltage, power, external_temperature, anomaly)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data.cpu_load, data.battery_charge, data.radiation_exposure,
                    data.temperature_interior, data.temperature_battery, data.communication_signal_strength,
                    data.system_status, data.voltage, data.power, data.external_temperature, int(prediction)
                ))

                connection.commit()
                cursor.close()
                connection.close()

                print("✅ Anomaly stored in MySQL!")  # Debug log

            except pymysql.MySQLError as db_err:
                return {"error": f"🚨 Database error: {str(db_err)}"}

        return {"anomaly": int(prediction)}

    except Exception as e:
        return {"error": f"⚠️ Prediction failed: {str(e)}"}

# ✅ Fetch Latest Sensor Data from MySQL
@app.get("/fetch-latest")
def fetch_latest_data():
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)  # ✅ Use DictCursor for better readability
        
        query = """
        SELECT cpu_load, battery_charge, radiation_exposure, 
               temperature_interior, temperature_battery, 
               communication_signal_strength, system_status, 
               voltage, power, external_temperature 
        FROM history 
        ORDER BY timestamp DESC LIMIT 1
        """
        cursor.execute(query)
        row = cursor.fetchone()
        
        cursor.close()
        connection.close()

        if row:
            return {"latest_data": row}
        else:
            return {"message": "⚠️ No data found!"}

    except Exception as e:
        return {"error": str(e)}

# ✅ Get the PORT environment variable (default: 8000)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
