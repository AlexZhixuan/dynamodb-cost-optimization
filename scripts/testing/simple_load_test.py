#!/usr/bin/env python3
"""Simple load testing for DynamoDB"""

import time
import random
from crud_operations import DynamoDBTester

def simple_load_test(duration_seconds=10, operations_per_second=5):
    """Run a simple load test"""
    tester = DynamoDBTester()
    
    print(f"\n=== Starting Load Test ===")
    print(f"Duration: {duration_seconds} seconds")
    print(f"Target: {operations_per_second} ops/second")
    
    start_time = time.time()
    total_ops = 0
    successful_ops = 0
    
    while time.time() - start_time < duration_seconds:
        for i in range(operations_per_second):
            try:
                # Random operation
                op_type = random.choice(['create', 'read'])
                product_id = f"LOAD_{random.randint(1000, 9999)}"
                
                if op_type == 'create':
                    success = tester.create_product(
                        product_id, 
                        f"Test Product {product_id}", 
                        random.uniform(10, 1000)
                    )
                else:
                    success = tester.read_product(product_id) is not None
                
                total_ops += 1
                if success:
                    successful_ops += 1
                    
            except Exception as e:
                print(f"Error: {e}")
                total_ops += 1
        
        time.sleep(1)  # Wait 1 second before next batch
    
    # Results
    duration = time.time() - start_time
    print(f"\n=== Load Test Results ===")
    print(f"Duration: {duration:.1f} seconds")
    print(f"Total Operations: {total_ops}")
    print(f"Successful: {successful_ops}")
    print(f"Failed: {total_ops - successful_ops}")
    print(f"Success Rate: {(successful_ops/total_ops*100):.1f}%")
    print(f"Actual ops/second: {total_ops/duration:.1f}")

if __name__ == "__main__":
    simple_load_test(duration_seconds=10, operations_per_second=5)
