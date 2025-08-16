#!/usr/bin/env python
import random
import string
from datetime import datetime, UTC
import boto3


def random_string(length=8):
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


def now_utc_sec():
    return int(datetime.now(UTC).strftime("%s"))


def now_utc_ms():
    return round(float(datetime.now(UTC).strftime("%s.%f")) * 1000)


def create_limit_table(table_name, index_name="idx"):
    """Tests which call this are expected to be in mock_aws context"""

    mock_client = boto3.client("dynamodb", region_name="us-east-1")
    key_schema = [
        {"AttributeName": "resourceName", "KeyType": "HASH"},
        {"AttributeName": "accountId", "KeyType": "RANGE"},
    ]

    attribute_definitions = [
        {"AttributeName": "resourceName", "AttributeType": "S"},
        {"AttributeName": "accountId", "AttributeType": "S"},
        {"AttributeName": "serviceName", "AttributeType": "S"},
    ]

    global_sec_indexes = [
        {
            "IndexName": index_name,
            "KeySchema": [{"AttributeName": "serviceName", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 123,
                "WriteCapacityUnits": 123,
            },
        }
    ]

    provisioned_throughput = {"ReadCapacityUnits": 123, "WriteCapacityUnits": 123}

    mock_client.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        GlobalSecondaryIndexes=global_sec_indexes,
        ProvisionedThroughput=provisioned_throughput,
    )

    return boto3.resource("dynamodb", "us-east-1").Table(table_name)


def create_non_fung_table(table_name, index_name="idx"):
    """Tests which call this are expected to be in mock_aws context"""

    mock_client = boto3.client("dynamodb", region_name="us-east-1")
    key_schema = [
        {"AttributeName": "resourceCoordinate", "KeyType": "HASH"},
        {"AttributeName": "reservationId", "KeyType": "RANGE"},
    ]

    attribute_definitions = [
        {"AttributeName": "resourceCoordinate", "AttributeType": "S"},
        {"AttributeName": "reservationId", "AttributeType": "S"},
        {"AttributeName": "resourceId", "AttributeType": "S"},
    ]

    global_sec_indexes = [
        {
            "IndexName": index_name,
            "KeySchema": [{"AttributeName": "resourceId", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 123,
                "WriteCapacityUnits": 123,
            },
        }
    ]

    provisioned_throughput = {"ReadCapacityUnits": 123, "WriteCapacityUnits": 123}

    mock_client.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        GlobalSecondaryIndexes=global_sec_indexes,
        ProvisionedThroughput=provisioned_throughput,
    )

    return boto3.resource("dynamodb", "us-east-1").Table(table_name)
