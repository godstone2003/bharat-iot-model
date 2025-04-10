import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.create_table(
    TableName='iot-input-table',
    KeySchema=[
        {'AttributeName': 'device_id', 'KeyType': 'HASH'},  # Partition key
        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}  # Sort key
    ],
    AttributeDefinitions=[
        {'AttributeName': 'device_id', 'AttributeType': 'S'},
        {'AttributeName': 'timestamp', 'AttributeType': 'S'}
    ],
    BillingMode='PAY_PER_REQUEST'
)

print("Creating table...")
table.meta.client.get_waiter('table_exists').wait(TableName='iot-input-table')
print("✅ Table created!")
