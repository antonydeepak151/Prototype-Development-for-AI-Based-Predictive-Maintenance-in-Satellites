import requests

# Fetch Latest Data
response = requests.get("http://127.0.0.1:8000/fetch-latest")
print(response.json())

# Predict (Modify the data payload)
data = {"sensor_value": 123}
response = requests.post("http://127.0.0.1:8000/predict", json=data)
print(response.json())
