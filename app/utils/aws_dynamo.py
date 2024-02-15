import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")


def create_table():
    table = dynamodb.create_table(
        TableName="chats",
        KeySchema=[
            {"AttributeName": "chat_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "chat_id", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    print("Table status:", table.table_status)


if __name__ == "__main__":
    create_table()
