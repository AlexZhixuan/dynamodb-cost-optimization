"""
Enhanced Load Testing Suite for DynamoDB
Tests multiple traffic scenarios and measures performance
"""

import boto3
import time
import random
from datetime import datetime
from decimal import Decimal
from collections import defaultdict

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ecommerce-products-dev')

# Test configuration
PRODUCT_ID_RANGE = (1, 500)  # TEST-PROD-0001 to TEST-PROD-0500


class LoadTestResult:
    """Store and analyze load test results"""
    
    def __init__(self, scenario_name):
        self.scenario_name = scenario_name
        self.operations = []
        self.errors = defaultdict(int)
        self.start_time = None
        self.end_time = None
    
    def record_operation(self, operation_type, success, latency_ms, error_type=None):
        """Record a single operation result"""
        self.operations.append({
            'type': operation_type,
            'success': success,
            'latency_ms': latency_ms,
            'timestamp': datetime.now()
        })
        
        if not success and error_type:
            self.errors[error_type] += 1
    
    def calculate_metrics(self):
        """Calculate performance metrics"""
        if not self.operations:
            return None
        
        total = len(self.operations)
        successful = sum(1 for op in self.operations if op['success'])
        failed = total - successful
        
        latencies = [op['latency_ms'] for op in self.operations if op['success']]
        
        if latencies:
            latencies.sort()
            p50 = latencies[len(latencies) // 2]
            p95 = latencies[int(len(latencies) * 0.95)]
            p99 = latencies[int(len(latencies) * 0.99)]
            avg = sum(latencies) / len(latencies)
        else:
            p50 = p95 = p99 = avg = 0
        
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        throughput = total / duration if duration > 0 else 0
        
        return {
            'total_operations': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'avg_latency_ms': avg,
            'p50_latency_ms': p50,
            'p95_latency_ms': p95,
            'p99_latency_ms': p99,
            'duration_sec': duration,
            'throughput_ops_sec': throughput,
            'errors': dict(self.errors)
        }
    
    def print_summary(self):
        """Print test results summary"""
        metrics = self.calculate_metrics()
        if not metrics:
            print("No operations recorded")
            return
        
        print(f"\n{'='*70}")
        print(f"Scenario: {self.scenario_name}")
        print(f"{'='*70}")
        print(f"Total Operations:     {metrics['total_operations']:,}")
        print(f"Successful:           {metrics['successful']:,} ({metrics['success_rate']:.1f}%)")
        print(f"Failed:               {metrics['failed']:,}")
        print(f"Duration:             {metrics['duration_sec']:.1f} seconds")
        print(f"Throughput:           {metrics['throughput_ops_sec']:.1f} ops/sec")
        print(f"\nLatency Metrics:")
        print(f"  Average:            {metrics['avg_latency_ms']:.1f} ms")
        print(f"  P50 (median):       {metrics['p50_latency_ms']:.1f} ms")
        print(f"  P95:                {metrics['p95_latency_ms']:.1f} ms")
        print(f"  P99:                {metrics['p99_latency_ms']:.1f} ms")
        
        if metrics['errors']:
            print(f"\nError Breakdown:")
            for error_type, count in metrics['errors'].items():
                print(f"  {error_type}: {count}")


def perform_read_operation(product_id):
    """
    Perform a single read operation
    Returns: (success, latency_ms, error_type)
    """
    start = time.time()
    try:
        response = table.get_item(Key={'product_id': product_id})
        latency = (time.time() - start) * 1000
        
        if 'Item' in response:
            return True, latency, None
        else:
            return False, latency, 'ItemNotFound'
            
    except Exception as e:
        latency = (time.time() - start) * 1000
        return False, latency, type(e).__name__


def perform_write_operation(product_id):
    """
    Perform a single write operation (update stock)
    Returns: (success, latency_ms, error_type)
    """
    start = time.time()
    try:
        new_stock = random.randint(0, 500)
        table.update_item(
            Key={'product_id': product_id},
            UpdateExpression='SET stock = :val',
            ExpressionAttributeValues={':val': new_stock}
        )
        latency = (time.time() - start) * 1000
        return True, latency, None
        
    except Exception as e:
        latency = (time.time() - start) * 1000
        return False, latency, type(e).__name__


def scenario_steady_traffic(ops_per_sec=50, duration_sec=60, read_ratio=0.8):
    """
    Scenario 1: Steady traffic
    Consistent operations per second for a fixed duration
    """
    result = LoadTestResult(f"Steady Traffic ({ops_per_sec} ops/sec for {duration_sec}s)")
    result.start_time = datetime.now()
    
    print(f"\n{'='*70}")
    print(f"Running: {result.scenario_name}")
    print(f"Read/Write Ratio: {read_ratio*100:.0f}%/{(1-read_ratio)*100:.0f}%")
    print(f"{'='*70}")
    
    total_ops = ops_per_sec * duration_sec
    ops_completed = 0
    
    for second in range(duration_sec):
        for _ in range(ops_per_sec):
            # Random product ID
            product_id = f'TEST-PROD-{random.randint(*PRODUCT_ID_RANGE):04d}'
            
            # Decide read or write based on ratio
            if random.random() < read_ratio:
                success, latency, error = perform_read_operation(product_id)
                result.record_operation('read', success, latency, error)
            else:
                success, latency, error = perform_write_operation(product_id)
                result.record_operation('write', success, latency, error)
            
            ops_completed += 1
        
        # Sleep to maintain rate (compensate for operation time)
        time.sleep(max(0, 1.0))
        
        # Progress indicator
        if (second + 1) % 10 == 0:
            print(f"Progress: {second + 1}/{duration_sec} seconds ({ops_completed}/{total_ops} ops)")
    
    result.end_time = datetime.now()
    result.print_summary()
    return result


def scenario_traffic_spike(base_ops=20, spike_ops=200, spike_duration_sec=30, read_ratio=0.8):
    """
    Scenario 2: Traffic spike
    Sudden increase from base to spike traffic
    """
    result = LoadTestResult(f"Traffic Spike ({base_ops} → {spike_ops} ops/sec)")
    result.start_time = datetime.now()
    
    print(f"\n{'='*70}")
    print(f"Running: {result.scenario_name}")
    print(f"Base: {base_ops} ops/sec | Spike: {spike_ops} ops/sec | Duration: {spike_duration_sec}s")
    print(f"{'='*70}")
    
    # Phase 1: Base traffic (30 seconds)
    print("\nPhase 1: Base traffic (30s)")
    for second in range(30):
        for _ in range(base_ops):
            product_id = f'TEST-PROD-{random.randint(*PRODUCT_ID_RANGE):04d}'
            
            if random.random() < read_ratio:
                success, latency, error = perform_read_operation(product_id)
                result.record_operation('read', success, latency, error)
            else:
                success, latency, error = perform_write_operation(product_id)
                result.record_operation('write', success, latency, error)
        
        time.sleep(max(0, 1.0))
        
        if (second + 1) % 10 == 0:
            print(f"  Progress: {second + 1}/30 seconds")
    
    # Phase 2: Spike traffic
    print(f"\nPhase 2: SPIKE traffic ({spike_duration_sec}s)")
    for second in range(spike_duration_sec):
        for _ in range(spike_ops):
            product_id = f'TEST-PROD-{random.randint(*PRODUCT_ID_RANGE):04d}'
            
            if random.random() < read_ratio:
                success, latency, error = perform_read_operation(product_id)
                result.record_operation('read', success, latency, error)
            else:
                success, latency, error = perform_write_operation(product_id)
                result.record_operation('write', success, latency, error)
        
        time.sleep(max(0, 1.0 / (spike_ops / base_ops)))
        
        if (second + 1) % 10 == 0:
            print(f"  Progress: {second + 1}/{spike_duration_sec} seconds")
    
    # Phase 3: Back to base (30 seconds)
    print("\nPhase 3: Return to base traffic (30s)")
    for second in range(30):
        for _ in range(base_ops):
            product_id = f'TEST-PROD-{random.randint(*PRODUCT_ID_RANGE):04d}'
            
            if random.random() < read_ratio:
                success, latency, error = perform_read_operation(product_id)
                result.record_operation('read', success, latency, error)
            else:
                success, latency, error = perform_write_operation(product_id)
                result.record_operation('write', success, latency, error)
        
        time.sleep(max(0, 1.0))
        
        if (second + 1) % 10 == 0:
            print(f"  Progress: {second + 1}/30 seconds")
    
    result.end_time = datetime.now()
    result.print_summary()
    return result


def scenario_gradual_increase(start_ops=10, end_ops=100, duration_sec=60, read_ratio=0.8):
    """
    Scenario 3: Gradual increase
    Linearly increase operations from start to end over duration
    """
    result = LoadTestResult(f"Gradual Increase ({start_ops} → {end_ops} ops/sec)")
    result.start_time = datetime.now()
    
    print(f"\n{'='*70}")
    print(f"Running: {result.scenario_name}")
    print(f"Duration: {duration_sec} seconds")
    print(f"{'='*70}")
    
    for second in range(duration_sec):
        # Calculate current ops/sec (linear increase)
        progress = second / duration_sec
        current_ops = int(start_ops + (end_ops - start_ops) * progress)
        
        for _ in range(current_ops):
            product_id = f'TEST-PROD-{random.randint(*PRODUCT_ID_RANGE):04d}'
            
            if random.random() < read_ratio:
                success, latency, error = perform_read_operation(product_id)
                result.record_operation('read', success, latency, error)
            else:
                success, latency, error = perform_write_operation(product_id)
                result.record_operation('write', success, latency, error)
        
        time.sleep(max(0, 1.0))
        
        if (second + 1) % 15 == 0:
            print(f"Progress: {second + 1}/{duration_sec} seconds (current: {current_ops} ops/sec)")
    
    result.end_time = datetime.now()
    result.print_summary()
    return result


def main():
    """Run all load test scenarios"""
    print("="*70)
    print("ENHANCED LOAD TESTING SUITE")
    print("="*70)
    print(f"Target table: {table.table_name}")
    print(f"Test data: TEST-PROD-0001 to TEST-PROD-0500")
    print(f"Start time: {datetime.now().isoformat()}")
    print("="*70)
    
    results = []
    
    # Scenario 1: Steady traffic
    print("\n\n>>> SCENARIO 1: Steady Traffic")
    result1 = scenario_steady_traffic(ops_per_sec=50, duration_sec=60, read_ratio=0.8)
    results.append(result1)
    
    print("\n\nWaiting 10 seconds before next scenario...")
    time.sleep(10)
    
    # Scenario 2: Traffic spike
    print("\n\n>>> SCENARIO 2: Traffic Spike")
    result2 = scenario_traffic_spike(base_ops=20, spike_ops=150, spike_duration_sec=30, read_ratio=0.8)
    results.append(result2)
    
    print("\n\nWaiting 10 seconds before next scenario...")
    time.sleep(10)
    
    # Scenario 3: Gradual increase
    print("\n\n>>> SCENARIO 3: Gradual Increase")
    result3 = scenario_gradual_increase(start_ops=10, end_ops=100, duration_sec=60, read_ratio=0.8)
    results.append(result3)
    
    # Final summary
    print("\n\n" + "="*70)
    print("ALL SCENARIOS COMPLETE - SUMMARY")
    print("="*70)
    
    for i, result in enumerate(results, 1):
        metrics = result.calculate_metrics()
        print(f"\nScenario {i}: {result.scenario_name}")
        print(f"  Success Rate: {metrics['success_rate']:.1f}%")
        print(f"  Avg Latency:  {metrics['avg_latency_ms']:.1f} ms")
        print(f"  P95 Latency:  {metrics['p95_latency_ms']:.1f} ms")
        print(f"  Throughput:   {metrics['throughput_ops_sec']:.1f} ops/sec")
    
    print("\n" + "="*70)
    print("Testing complete!")
    print(f"End time: {datetime.now().isoformat()}")
    print("="*70)


if __name__ == "__main__":
    main()
