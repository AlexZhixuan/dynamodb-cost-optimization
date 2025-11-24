"""
CloudWatch Metrics and Cost Analysis
Retrieves actual DynamoDB metrics and calculates real costs
"""

import boto3
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize clients
cloudwatch = boto3.client('cloudwatch')
dynamodb = boto3.client('dynamodb')

TABLE_NAME = 'ecommerce-products-dev'
REGION = 'us-east-1'

# DynamoDB Pricing (us-east-1, On-Demand)
ON_DEMAND_READ_PRICE = 0.25 / 1_000_000  # per read request unit
ON_DEMAND_WRITE_PRICE = 1.25 / 1_000_000  # per write request unit


def get_consumed_capacity(minutes=30):
    """
    Get consumed read and write capacity from CloudWatch
    
    Args:
        minutes (int): Number of minutes to look back
    
    Returns:
        dict: Consumed RCUs and WCUs
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=minutes)
    
    print(f"Fetching metrics from {start_time} to {end_time}")
    print(f"Time range: {minutes} minutes")
    
    # Get ConsumedReadCapacityUnits
    read_response = cloudwatch.get_metric_statistics(
        Namespace='AWS/DynamoDB',
        MetricName='ConsumedReadCapacityUnits',
        Dimensions=[
            {'Name': 'TableName', 'Value': TABLE_NAME}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,  # 1 minute intervals
        Statistics=['Sum']
    )
    
    # Get ConsumedWriteCapacityUnits
    write_response = cloudwatch.get_metric_statistics(
        Namespace='AWS/DynamoDB',
        MetricName='ConsumedWriteCapacityUnits',
        Dimensions=[
            {'Name': 'TableName', 'Value': TABLE_NAME}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=['Sum']
    )
    
    # Sum up all datapoints
    total_rcus = sum(dp['Sum'] for dp in read_response['Datapoints'])
    total_wcus = sum(dp['Sum'] for dp in write_response['Datapoints'])
    
    return {
        'read_capacity_units': total_rcus,
        'write_capacity_units': total_wcus,
        'datapoints_count': len(read_response['Datapoints']),
        'start_time': start_time,
        'end_time': end_time
    }


def calculate_on_demand_cost(rcus, wcus):
    """
    Calculate On-Demand cost for consumed capacity
    
    Args:
        rcus (float): Total read capacity units consumed
        wcus (float): Total write capacity units consumed
    
    Returns:
        dict: Cost breakdown
    """
    read_cost = rcus * ON_DEMAND_READ_PRICE
    write_cost = wcus * ON_DEMAND_WRITE_PRICE
    total_cost = read_cost + write_cost
    
    return {
        'read_cost': read_cost,
        'write_cost': write_cost,
        'total_cost': total_cost
    }


def get_table_info():
    """Get current table information"""
    response = dynamodb.describe_table(TableName=TABLE_NAME)
    table = response['Table']
    
    return {
        'status': table['TableStatus'],
        'item_count': table.get('ItemCount', 0),
        'size_bytes': table.get('TableSizeBytes', 0),
        'billing_mode': table.get('BillingModeSummary', {}).get('BillingMode', 'N/A')
    }


def main():
    """Main function to analyze CloudWatch metrics and costs"""
    print("="*70)
    print("CLOUDWATCH METRICS & COST ANALYSIS")
    print("="*70)
    print(f"Table: {TABLE_NAME}")
    print(f"Region: {REGION}")
    print(f"Analysis Time: {datetime.now().isoformat()}")
    print("="*70)
    
    # Get table info
    print("\nTable Information:")
    print("-"*70)
    table_info = get_table_info()
    print(f"Status:        {table_info['status']}")
    print(f"Billing Mode:  {table_info['billing_mode']}")
    print(f"Item Count:    {table_info['item_count']:,}")
    print(f"Table Size:    {table_info['size_bytes'] / 1024 / 1024:.2f} MB")
    
    # Get metrics for last 30 minutes (covering our load tests)
    print("\n" + "="*70)
    print("CONSUMED CAPACITY METRICS (Last 30 Minutes)")
    print("="*70)
    
    metrics = get_consumed_capacity(minutes=30)
    
    if metrics['datapoints_count'] == 0:
        print("\n⚠️  No metrics data available yet.")
        print("   CloudWatch metrics may take 5-10 minutes to appear.")
        print("   Please wait a few minutes and run this script again.")
        return
    
    print(f"\nDatapoints collected: {metrics['datapoints_count']}")
    print(f"Time range: {metrics['start_time']} to {metrics['end_time']}")
    print(f"\nConsumed Capacity:")
    print(f"  Read Capacity Units:  {metrics['read_capacity_units']:,.1f} RCUs")
    print(f"  Write Capacity Units: {metrics['write_capacity_units']:,.1f} WCUs")
    
    # Calculate costs
    print("\n" + "="*70)
    print("COST ANALYSIS (On-Demand Pricing)")
    print("="*70)
    
    costs = calculate_on_demand_cost(
        metrics['read_capacity_units'],
        metrics['write_capacity_units']
    )
    
    print(f"\nCost Breakdown:")
    print(f"  Read Operations:  ${costs['read_cost']:.6f}")
    print(f"  Write Operations: ${costs['write_cost']:.6f}")
    print(f"  {'─'*40}")
    print(f"  Total Cost:       ${costs['total_cost']:.6f}")
    
    # Project monthly costs
    minutes_in_month = 30 * 24 * 60
    scale_factor = minutes_in_month / 30
    
    monthly_rcus = metrics['read_capacity_units'] * scale_factor
    monthly_wcus = metrics['write_capacity_units'] * scale_factor
    monthly_costs = calculate_on_demand_cost(monthly_rcus, monthly_wcus)
    
    print(f"\n" + "="*70)
    print("PROJECTED MONTHLY COSTS")
    print("="*70)
    print(f"(Based on current traffic pattern)")
    print(f"\nProjected Monthly Consumption:")
    print(f"  Read Capacity Units:  {monthly_rcus:,.0f} RCUs")
    print(f"  Write Capacity Units: {monthly_wcus:,.0f} WCUs")
    print(f"\nProjected Monthly Cost:")
    print(f"  Read Operations:  ${monthly_costs['read_cost']:.2f}")
    print(f"  Write Operations: ${monthly_costs['write_cost']:.2f}")
    print(f"  {'─'*40}")
    print(f"  Total:            ${monthly_costs['total_cost']:.2f}")
    
    # Summary
    print(f"\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    
    total_capacity = metrics['read_capacity_units'] + metrics['write_capacity_units']
    if total_capacity > 0:
        read_ratio = metrics['read_capacity_units'] / total_capacity
        print(f"\n✓ Read/Write Ratio: {read_ratio*100:.1f}% reads / {(1-read_ratio)*100:.1f}% writes")
    
    print(f"✓ Actual test cost: ${costs['total_cost']:.6f} for {metrics['datapoints_count']} minutes")
    if metrics['datapoints_count'] > 0:
        print(f"✓ Cost per minute: ${costs['total_cost']/metrics['datapoints_count']:.6f}")
    
    if monthly_costs['total_cost'] < 50:
        print(f"\n💡 RECOMMENDATION: On-Demand pricing is cost-effective for this traffic level")
        print(f"   Monthly cost under $50 makes On-Demand the optimal choice")
    else:
        print(f"\n💡 RECOMMENDATION: Consider Provisioned capacity for cost savings")
        print(f"   Monthly cost over $50 - Provisioned may save 40-60%")
    
    print("\n" + "="*70)
    print("Analysis Complete")
    print("="*70)


if __name__ == "__main__":
    main()
