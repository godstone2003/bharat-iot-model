import json
import boto3
import datetime
from decimal import Decimal  # ✅ Required for DynamoDB number handling

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('iot-input-table')  # Or your actual table name

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        item = {
            'device_id': str(body['device_id']),
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'light': Decimal(str(body['light'])),        # ✅ Convert to Decimal
            'co2': Decimal(str(body['co2'])),
            'humidity': Decimal(str(body['humidity'])),
            'motion': Decimal(str(body['motion'])),
            'vibration': Decimal(str(body['vibration'])),
            'minute': Decimal(str(body['minute'])),
            'hour': Decimal(str(body['hour'])),
            'dayofweek': Decimal(str(body['dayofweek'])),
            'prediction_status': 'pending'
        }

        table.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'IoT data saved successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
