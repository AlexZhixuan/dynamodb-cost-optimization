#!/usr/bin/env python3
"""CRUD operations for DynamoDB testing"""

import boto3
import os
import time
import json
from dotenv import load_dotenv
from decimal import Decimal
from botocore.exceptions import ClientError

load_dotenv()

class DynamoDBTester:
    def __init__(self, table_name='products-demo'):
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
            region_name='us-east-1'
        )
        self.table = self.dynamodb.Table(table_name)
    
    def create_product(self, product_id, name, price, category="Electronics"):
        """Create a product"""
        try:
            response = self.table.put_item(
                Item={
                    'product_id': product_id,
                    'name': name,
                    'price': Decimal(str(price)),
                    'category': category,
                    'timestamp': int(time.time())
                }
            )
            print(f"Created product: {product_id}")
            return True
        except Exception as e:
            print(f"Error creating product: {e}")
            return False
    
    def read_product(self, product_id):
        """Read a product"""
        try:
            response = self.table.get_item(Key={'product_id': product_id})
            if 'Item' in response:
                print(f"Found product: {response['Item']}")
                return response['Item']
            else:
                print(f"Product {product_id} not found")
                return None
        except Exception as e:
            print(f"Error reading product: {e}")
            return None
    
    def update_product_price(self, product_id, new_price):
        """Update product price"""
        try:
            response = self.table.update_item(
                Key={'product_id': product_id},
                UpdateExpression='SET price = :price',
                ExpressionAttributeValues={':price': Decimal(str(new_price))},
                ReturnValues='UPDATED_NEW'
            )
            print(f"Updated product {product_id} price to {new_price}")
            return True
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
    
    def delete_product(self, product_id):
        """Delete a product"""
        try:
            response = self.table.delete_item(Key={'product_id': product_id})
            print(f"Deleted product: {product_id}")
            return True
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
    
    def list_all_products(self):
        """List all products"""
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            print(f"Found {len(items)} products")
            return items
        except Exception as e:
            print(f"Error listing products: {e}")
            return []

def test_crud():
    """Test all CRUD operations"""
    tester = DynamoDBTester()
    
    print("\n=== Testing CRUD Operations ===\n")
    
    # Create
    print("1. CREATE TEST:")
    tester.create_product("PROD001", "Laptop", 999.99)
    tester.create_product("PROD002", "Mouse", 29.99)
    
    # Read
    print("\n2. READ TEST:")
    tester.read_product("PROD001")
    
    # Update
    print("\n3. UPDATE TEST:")
    tester.update_product_price("PROD001", 899.99)
    
    # List
    print("\n4. LIST TEST:")
    products = tester.list_all_products()
    
    # Delete
    print("\n5. DELETE TEST:")
    tester.delete_product("PROD002")
    
    print("\n=== CRUD Tests Complete ===")

if __name__ == "__main__":
    test_crud()
