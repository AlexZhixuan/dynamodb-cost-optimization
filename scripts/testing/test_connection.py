#!/usr/bin/env python3
"""
Test DynamoDB Connection
Author: Andrea
"""

import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Loading Environment Variables
load_dotenv()

def test_connection():
    """Testing AWS DynamoDB connection"""
    try:
        # Fetching credentials from environment varaibles
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
            region_name='us-east-1'
        )
        
        # Listing all  tables
        tables = list(dynamodb.tables.all())
        
        print("Successfully connected to DynamoDB!")
        print(f"Found {len(tables)} table(s):")
        for table in tables:
            print(f"  - {table.name}")
            
        return True
        
    except ClientError as e:
        print(f"Connection failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
