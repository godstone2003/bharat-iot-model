from flask import Flask, render_template
import joblib
import numpy as np
import boto3
from boto3.dynamodb.conditions import Attr
import json

app = Flask(__name__)

# Load the trained model
model = joblib.load("random_forest_iot_model.pkl")

# DynamoDB Setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # e.g., 'us-east-1'
table = dynamodb.Table('iot-input-table')  # Your DynamoDB table name

@app.route("/")
def home():
    return "<h2>Welcome to IoT Prediction Service</h2><br><a href='/predict'>Predict from Latest IoT Data</a>"

@app.route("/predict", methods=["GET"])
def predict():
    try:
        # Fetch latest unprocessed item
        response = table.scan(
            FilterExpression=Attr('prediction_status').eq('pending')
        )
        items = response.get('Items', [])
        if not items:
            return "No new data to predict."

        # Pick the first unprocessed item
        item = sorted(items, key=lambda x: x['timestamp'], reverse=True)[0]

        # Extract features
        features = [
            float(item['light']),
            float(item['co2']),
            float(item['humidity']),
            float(item['motion']),
            float(item['vibration']),
            float(item['minute']),
            float(item['hour']),
            float(item['device_id']),
            float(item['dayofweek']),
        ]

        input_array = np.array([features])
        prediction = model.predict(input_array)[0]

        # Update item in DynamoDB (optional)
        table.update_item(
            Key={
                'device_id': item['device_id'],
                'timestamp': item['timestamp']
            },
            UpdateExpression="set prediction_status = :status, prediction_result = :pred",
            ExpressionAttributeValues={
                ':status': 'done',
                ':pred': str(prediction)
            }
        )

        return render_template("result.html", prediction=prediction)

    except Exception as e:
        return f"❌ Error in prediction: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
