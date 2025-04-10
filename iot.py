import boto3
import json
import random
import time
from datetime import datetime

# AWS Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')  # e.g., 'us-east-1'

# Lambda function name (not the ARN, just the name or alias)
lambda_function_name = 'bharat-lamda-funtion'

def simulate_iot_input():
    now = datetime.now()

    payload = {
        'device_id': 5000,
        'light': round(random.uniform(100.0, 900.0), 2),
        'co2': round(random.uniform(300.0, 800.0), 2),
        'humidity': round(random.uniform(20.0, 70.0), 2),
        'motion': round(random.uniform(0, 1), 2),
        'vibration': round(random.uniform(0, 1), 2),
        'minute': now.minute,
        'hour': now.hour,
        'dayofweek': now.weekday()
    }

    response = lambda_client.invoke(
        FunctionName=lambda_function_name,
        InvocationType='RequestResponse',  # Or 'Event' for async
        Payload=json.dumps({ 'body': json.dumps(payload) }),
    )

    result = json.load(response['Payload'])
    print(f"🔁 Sent data: {payload}")
    print(f"✅ Lambda response: {result}")

if __name__ == "__main__":
    while True:
        simulate_iot_input()
        time.sleep(10)
