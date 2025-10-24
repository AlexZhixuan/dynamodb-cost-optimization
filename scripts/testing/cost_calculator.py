#!/usr/bin/env python3
"""Simple DynamoDB cost calculator"""

def calculate_cost(read_ops, write_ops, storage_gb=0.5):
    """Calculate DynamoDB costs for On-Demand and Provisioned"""
    
    # On-Demand pricing
    on_demand_read = read_ops * 0.25 / 1_000_000  # $0.25 per million
    on_demand_write = write_ops * 1.25 / 1_000_000  # $1.25 per million
    on_demand_storage = storage_gb * 0.25  # $0.25 per GB
    on_demand_total = on_demand_read + on_demand_write + on_demand_storage
    
    # Provisioned pricing (estimate)
    # Assuming we need 1 RCU per 2 reads/sec, 1 WCU per write/sec
    rcu_needed = max(1, read_ops // 2 // 3600)  # per hour
    wcu_needed = max(1, write_ops // 3600)
    provisioned_read = rcu_needed * 0.00065 * 24 * 30  # monthly
    provisioned_write = wcu_needed * 0.00325 * 24 * 30
    provisioned_storage = storage_gb * 0.25
    provisioned_total = provisioned_read + provisioned_write + provisioned_storage
    
    print("\n=== DynamoDB Cost Analysis ===")
    print(f"Based on {read_ops:,} reads and {write_ops:,} writes per month")
    print(f"Storage: {storage_gb} GB\n")
    
    print("On-Demand Pricing:")
    print(f"  Read cost:    ${on_demand_read:.2f}")
    print(f"  Write cost:   ${on_demand_write:.2f}")
    print(f"  Storage cost: ${on_demand_storage:.2f}")
    print(f"  Total:        ${on_demand_total:.2f}/month\n")
    
    print("Provisioned Pricing (estimated):")
    print(f"  RCUs needed: {rcu_needed}")
    print(f"  WCUs needed: {wcu_needed}")
    print(f"  Total:       ${provisioned_total:.2f}/month\n")
    
    savings = (on_demand_total - provisioned_total) / on_demand_total * 100
    if savings > 0:
        print(f"Provisioned saves {savings:.1f}% for this workload")
    else:
        print(f"On-Demand is cheaper for this workload")

if __name__ == "__main__":
    # Test scenarios
    print("Scenario 1: Low traffic (100 ops/sec)")
    calculate_cost(read_ops=80*100*3600*24*30, write_ops=20*100*3600*24*30)
    
    print("\n" + "="*40)
    print("\nScenario 2: Black Friday (1000 ops/sec for 1 day)")
    calculate_cost(read_ops=800*1000*3600*24, write_ops=200*1000*3600*24)
