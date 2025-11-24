"""
Setup Test Data for DynamoDB Load Testing
Populates the table with realistic product data for testing
"""

import boto3
from datetime import datetime
import random
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ecommerce-products-dev')

# Product categories and sample data
CATEGORIES = ['Electronics', 'Books', 'Clothing', 'Home & Kitchen', 'Sports', 'Toys']

PRODUCT_NAMES = {
    'Electronics': ['Wireless Mouse', 'USB Cable', 'Laptop Stand', 'Keyboard', 'Webcam', 'Headphones'],
    'Books': ['Python Guide', 'Cloud Computing', 'Data Science', 'Fiction Novel', 'Biography', 'Cookbook'],
    'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Sneakers', 'Hat', 'Dress'],
    'Home & Kitchen': ['Coffee Maker', 'Blender', 'Plates Set', 'Storage Box', 'Lamp', 'Pillow'],
    'Sports': ['Yoga Mat', 'Dumbbells', 'Running Shoes', 'Water Bottle', 'Resistance Bands', 'Jump Rope'],
    'Toys': ['Building Blocks', 'Puzzle', 'Action Figure', 'Board Game', 'Stuffed Animal', 'Craft Kit']
}


def generate_test_products(count=500):
    """
    Generate test product data
    
    Args:
        count (int): Number of products to generate
    
    Returns:
        list: List of product dictionaries
    """
    products = []
    
    for i in range(1, count + 1):
        category = random.choice(CATEGORIES)
        product_base_name = random.choice(PRODUCT_NAMES[category])
        
        product = {
            'product_id': f'TEST-PROD-{i:04d}',
            'name': f'{product_base_name} - Model {i}',
            'price': Decimal(str(round(random.uniform(9.99, 999.99), 2))),
            'category': category,
            'stock': random.randint(0, 500),
            'description': f'Test product for load testing - {category} item #{i}',
            'created_at': datetime.now().isoformat(),
            'is_test_data': True  # Flag to identify test data for cleanup
        }
        
        products.append(product)
    
    return products


def batch_write_products(products, batch_size=25):
    """
    Write products to DynamoDB in batches
    DynamoDB batch_writer handles batching automatically
    
    Args:
        products (list): List of product dictionaries
        batch_size (int): Items per batch (max 25 for DynamoDB)
    """
    success_count = 0
    error_count = 0
    
    print(f"Writing {len(products)} products to DynamoDB...")
    print(f"Table: {table.table_name}")
    print(f"{'='*60}")
    
    try:
        with table.batch_writer() as batch:
            for i, product in enumerate(products, 1):
                try:
                    batch.put_item(Item=product)
                    success_count += 1
                    
                    # Progress indicator
                    if i % 50 == 0:
                        print(f"Progress: {i}/{len(products)} products written...")
                        
                except Exception as e:
                    error_count += 1
                    print(f"Error writing product {product['product_id']}: {e}")
        
        print(f"{'='*60}")
        print(f"✓ Successfully wrote {success_count} products")
        if error_count > 0:
            print(f"✗ Failed to write {error_count} products")
            
    except Exception as e:
        print(f"✗ Batch write error: {e}")
        raise


def verify_data():
    """
    Verify that test data was written successfully
    """
    print(f"\n{'='*60}")
    print("Verifying test data...")
    print(f"{'='*60}")
    
    try:
        # Try to read a few test products
        test_ids = ['TEST-PROD-0001', 'TEST-PROD-0050', 'TEST-PROD-0100']
        
        for product_id in test_ids:
            response = table.get_item(Key={'product_id': product_id})
            if 'Item' in response:
                item = response['Item']
                print(f"✓ Found {product_id}: {item['name']} - ${item['price']}")
            else:
                print(f"✗ Could not find {product_id}")
        
        print(f"{'='*60}")
        print("✓ Verification complete")
        
    except Exception as e:
        print(f"✗ Verification error: {e}")


def main():
    """
    Main function to setup test data
    """
    print("="*60)
    print("DynamoDB Test Data Setup")
    print("="*60)
    print(f"Target table: {table.table_name}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*60)
    
    # Configuration
    num_products = 500  # Adjust this number based on your testing needs
    
    print(f"\nGenerating {num_products} test products...")
    products = generate_test_products(num_products)
    print(f"✓ Generated {len(products)} products")
    
    # Confirm before writing
    print(f"\nReady to write {len(products)} products to DynamoDB.")
    confirm = input("Continue? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Setup cancelled.")
        return
    
    # Write to DynamoDB
    batch_write_products(products)
    
    # Verify
    verify_data()
    
    print("\n" + "="*60)
    print("Test Data Setup Complete!")
    print("="*60)
    print(f"\nYou can now run load tests against these {num_products} products.")
    print("Product IDs range: TEST-PROD-0001 to TEST-PROD-{:04d}".format(num_products))
    print("\nTo cleanup test data later, use cleanup_test_data.py")


if __name__ == "__main__":
    main()
