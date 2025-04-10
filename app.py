from flask import Flask, render_template
import joblib
import numpy as np
import boto3
from boto3.dynamodb.conditions import Attr
import json

app = Flask(__name__)

# Load the trained model
model = joblib.load("random_forest_iot_model.pkl")

# DynamoDB setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Replace with your AWS region
table = dynamodb.Table('iot-input-table')  # Replace with your table name

@app.route("/")
def home():
    return "<h2>Welcome to IoT Prediction Service</h2><br><a href='/predict'>Predict from Latest IoT Data</a>"

@app.route("/predict", methods=["GET"])
def predict():
    try:
        # Scan for unprocessed data
        response = table.scan(
            FilterExpression=Attr('prediction_status').eq('pending')
        )
        items = response.get('Items', [])
        if not items:
            return "No new data to predict."

        # Pick the latest item
        item = sorted(items, key=lambda x: x['timestamp'], reverse=True)[0]

        # Map device_id to a numeric value (temporary fix)
        device_mapping = {
            'sensor-001': 1,
            'sensor-002': 2,
            'sensor-003': 3
        }
        device_numeric = device_mapping.get(item['device_id'], 0)

        # Prepare input features (9 total including numeric device_id)
        features = [
            float(item['light']),
            float(item['co2']),
            float(item['humidity']),
            float(item['motion']),
            float(item['vibration']),
            float(item['minute']),
            float(item['hour']),
            float(item['dayofweek']),
            float(device_numeric)  # used instead of raw device_id
        ]

        input_array = np.array([features])
        prediction = model.predict(input_array)[0]

        # Update item with prediction result
        table.update_item(
            Key={
                'device_id': item['device_id'],
                'timestamp': item['timestamp']
            },
            UpdateExpression="SET prediction_status = :status, prediction_result = :pred",
            ExpressionAttributeValues={
                ':status': 'done',
                ':pred': str(prediction)
            }
        )

        return render_template("result.html", prediction=prediction)

    except Exception as e:
        return f"❌ Error in prediction: {str(e)}"

#if __name__ == "__main__":
    #app.run(debug=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)