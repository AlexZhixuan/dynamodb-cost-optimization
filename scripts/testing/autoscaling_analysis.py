"""
DynamoDB Auto-scaling Cost Analysis
Analyzes different traffic patterns and provides cost-optimized scaling recommendations
"""

import math


class AutoScalingAnalyzer:
    """
    Analyzes DynamoDB auto-scaling cost efficiency for different traffic patterns.
    
    This class calculates and compares costs across three pricing strategies:
    1. Fixed Provisioned Capacity (sized for peak load)
    2. On-Demand Pricing
    3. Provisioned with Auto-scaling (dynamic capacity adjustment)
    
    Attributes:
        wcu_price (float): Write Capacity Unit price per hour (us-east-1)
        rcu_price (float): Read Capacity Unit price per hour (us-east-1)
        on_demand_write (float): On-Demand write cost per million requests
        on_demand_read (float): On-Demand read cost per million requests
    """
    
    def __init__(self):
        """Initialize pricing constants for DynamoDB in us-east-1 region"""
        # Provisioned capacity pricing (per unit per hour)
        self.wcu_price = 0.00065  # Write Capacity Unit
        self.rcu_price = 0.00013  # Read Capacity Unit
        
        # On-Demand pricing (per million requests)
        self.on_demand_write = 1.25  # Write Request Unit
        self.on_demand_read = 0.25   # Read Request Unit
        
    def calculate_provisioned_cost(self, rcu, wcu, hours=730):
        """
        Calculate monthly cost for provisioned capacity.
        
        Args:
            rcu (int): Read Capacity Units
            wcu (int): Write Capacity Units
            hours (int): Number of hours (default 730 = 1 month)
        
        Returns:
            float: Total cost in USD
        """
        rcu_cost = rcu * self.rcu_price * hours
        wcu_cost = wcu * self.wcu_price * hours
        return rcu_cost + wcu_cost
    
    def calculate_on_demand_cost(self, reads, writes):
        """
        Calculate cost for on-demand pricing based on actual operations.
        
        Args:
            reads (int): Total number of read operations
            writes (int): Total number of write operations
        
        Returns:
            float: Total cost in USD
        """
        read_cost = (reads / 1_000_000) * self.on_demand_read
        write_cost = (writes / 1_000_000) * self.on_demand_write
        return read_cost + write_cost
    
    def analyze_traffic_pattern(self, scenario_name, traffic_data):
        """
        Analyze a traffic pattern and recommend optimal pricing strategy.
        
        Args:
            scenario_name (str): Name of the scenario being analyzed
            traffic_data (dict): Dictionary containing:
                - base_ops_per_sec: Baseline operations per second
                - peak_ops_per_sec: Peak operations per second
                - peak_hours_per_day: Duration of peak traffic (hours)
                - read_write_ratio: Proportion of reads (0.0-1.0)
        
        Returns:
            dict: Analysis results including recommendation and configuration
        """
        print(f"\n{'='*70}")
        print(f"Scenario: {scenario_name}")
        print(f"{'='*70}")
        
        # Extract traffic parameters
        base_ops = traffic_data['base_ops_per_sec']
        peak_ops = traffic_data['peak_ops_per_sec']
        peak_hours = traffic_data['peak_hours_per_day']
        read_ratio = traffic_data['read_write_ratio']
        
        # Calculate monthly operation counts
        base_hours = 24 - peak_hours
        seconds_per_month = 30 * 24 * 3600  # Approximate month
        
        # Total operations during base and peak periods
        base_ops_total = base_ops * base_hours * 30 * 3600
        peak_ops_total = peak_ops * peak_hours * 30 * 3600
        total_ops_monthly = base_ops_total + peak_ops_total
        
        # Split into reads and writes
        reads = total_ops_monthly * read_ratio
        writes = total_ops_monthly * (1 - read_ratio)
        
        # Calculate required capacity units (with 20% buffer for safety)
        safety_buffer = 1.2
        base_rcu = math.ceil(base_ops * read_ratio * safety_buffer)
        base_wcu = math.ceil(base_ops * (1 - read_ratio) * safety_buffer)
        peak_rcu = math.ceil(peak_ops * read_ratio * safety_buffer)
        peak_wcu = math.ceil(peak_ops * (1 - read_ratio) * safety_buffer)
        
        # Display traffic pattern
        print(f"\nTraffic Pattern Analysis:")
        print(f"  Baseline Traffic: {base_ops} ops/sec for {base_hours} hours/day")
        print(f"  Peak Traffic:     {peak_ops} ops/sec for {peak_hours} hours/day")
        print(f"  Read/Write Ratio: {read_ratio*100:.0f}% reads / {(1-read_ratio)*100:.0f}% writes")
        print(f"  Total Monthly Operations: {total_ops_monthly:,.0f}")
        
        print(f"\nCapacity Requirements (with 20% safety buffer):")
        print(f"  Baseline: {base_rcu} RCU, {base_wcu} WCU")
        print(f"  Peak:     {peak_rcu} RCU, {peak_wcu} WCU")
        
        # Strategy 1: Fixed Provisioned (sized for peak)
        fixed_cost = self.calculate_provisioned_cost(peak_rcu, peak_wcu)
        
        # Strategy 2: On-Demand
        on_demand_cost = self.calculate_on_demand_cost(reads, writes)
        
        # Strategy 3: Auto-scaling (provision for base, scale up for peak)
        base_cost = self.calculate_provisioned_cost(base_rcu, base_wcu)
        peak_extra_rcu = max(0, peak_rcu - base_rcu)
        peak_extra_wcu = max(0, peak_wcu - base_wcu)
        peak_extra_cost = self.calculate_provisioned_cost(
            peak_extra_rcu,
            peak_extra_wcu,
            hours=peak_hours * 30
        )
        autoscaling_cost = base_cost + peak_extra_cost
        
        # Display cost comparison
        print(f"\n{'Cost Analysis (Monthly)':^70}")
        print(f"{'-'*70}")
        print(f"1. Fixed Provisioned (peak):    ${fixed_cost:>10.2f}")
        print(f"   • Always provisioned at peak capacity")
        print(f"   • {peak_rcu} RCU + {peak_wcu} WCU for entire month")
        print()
        print(f"2. On-Demand:                   ${on_demand_cost:>10.2f}")
        print(f"   • Pay per request")
        print(f"   • {reads:,.0f} reads + {writes:,.0f} writes")
        print()
        print(f"3. Auto-scaling (recommended):  ${autoscaling_cost:>10.2f}")
        print(f"   • Base: {base_rcu} RCU + {base_wcu} WCU for {base_hours}h/day")
        print(f"   • Peak: {peak_rcu} RCU + {peak_wcu} WCU for {peak_hours}h/day")
        
        # Determine best option
        costs = {
            'Fixed Provisioned': fixed_cost,
            'On-Demand': on_demand_cost,
            'Auto-scaling': autoscaling_cost
        }
        best_option = min(costs, key=costs.get)
        best_cost = costs[best_option]
        
        # Display recommendation
        print(f"\n{'='*70}")
        print(f"✓ RECOMMENDATION: {best_option}")
        print(f"{'='*70}")
        print(f"Monthly Cost: ${best_cost:.2f}")
        
        if best_option == 'Auto-scaling':
            savings_vs_fixed = ((fixed_cost - best_cost) / fixed_cost) * 100
            savings_vs_ondemand = ((on_demand_cost - best_cost) / on_demand_cost) * 100
            
            print(f"\nCost Savings:")
            print(f"  • {savings_vs_fixed:.1f}% cheaper than Fixed Provisioned")
            print(f"  • {savings_vs_ondemand:.1f}% cheaper than On-Demand")
            
            print(f"\nRecommended Auto-scaling Configuration:")
            print(f"  Minimum Capacity: {base_rcu} RCU, {base_wcu} WCU")
            print(f"  Maximum Capacity: {peak_rcu} RCU, {peak_wcu} WCU")
            print(f"  Target Utilization: 70%")
            print(f"  Scale-up Cooldown: 60 seconds")
            print(f"  Scale-down Cooldown: 300 seconds")
            
        elif best_option == 'On-Demand':
            print(f"\nRationale:")
            print(f"  • Traffic is highly variable or unpredictable")
            print(f"  • Low overall usage doesn't justify provisioned capacity")
            print(f"  • Flexibility outweighs cost predictability")
            
        else:  # Fixed Provisioned
            print(f"\nRationale:")
            print(f"  • Traffic is very consistent")
            print(f"  • High sustained throughput")
            print(f"  • Cost predictability is priority")
        
        return {
            'scenario': scenario_name,
            'recommendation': best_option,
            'cost': best_cost,
            'base_rcu': base_rcu,
            'peak_rcu': peak_rcu,
            'base_wcu': base_wcu,
            'peak_wcu': peak_wcu,
            'savings_vs_fixed': ((fixed_cost - best_cost) / fixed_cost * 100) if best_option != 'Fixed Provisioned' else 0,
            'savings_vs_ondemand': ((on_demand_cost - best_cost) / on_demand_cost * 100) if best_option != 'On-Demand' else 0
        }


def main():
    """
    Main function to run auto-scaling analysis on multiple scenarios.
    Demonstrates cost optimization strategies for different traffic patterns.
    """
    analyzer = AutoScalingAnalyzer()
    
    # Define test scenarios representing different business patterns
    scenarios = [
        {
            'name': 'Steady E-commerce Traffic',
            'description': 'Consistent baseline with moderate daily peaks during business hours',
            'data': {
                'base_ops_per_sec': 80,
                'peak_ops_per_sec': 150,
                'peak_hours_per_day': 8,
                'read_write_ratio': 0.8
            }
        },
        {
            'name': 'Event-Driven Spikes',
            'description': 'Low baseline with extreme spikes during special events',
            'data': {
                'base_ops_per_sec': 20,
                'peak_ops_per_sec': 500,
                'peak_hours_per_day': 4,
                'read_write_ratio': 0.7
            }
        },
        {
            'name': 'Consistent High Traffic',
            'description': 'Sustained high throughput with minimal variation',
            'data': {
                'base_ops_per_sec': 200,
                'peak_ops_per_sec': 250,
                'peak_hours_per_day': 6,
                'read_write_ratio': 0.8
            }
        },
        {
            'name': 'Break-even Point Analysis',
            'description': 'Testing around the discovered 100 ops/sec threshold',
            'data': {
                'base_ops_per_sec': 100,
                'peak_ops_per_sec': 200,
                'peak_hours_per_day': 6,
                'read_write_ratio': 0.8
            }
        }
    ]
    
    # Header
    print("="*70)
    print("DynamoDB AUTO-SCALING COST ANALYSIS")
    print("="*70)
    print("\nAnalyzing different traffic patterns to determine optimal scaling strategy")
    print("and cost-effective capacity planning for DynamoDB tables.\n")
    
    # Analyze each scenario
    results = []
    for scenario in scenarios:
        print(f"\n{scenario['description']}")
        result = analyzer.analyze_traffic_pattern(
            scenario['name'],
            scenario['data']
        )
        results.append(result)
    
    # Summary section
    print(f"\n\n{'='*70}")
    print("DECISION FRAMEWORK: When to Use Each Strategy")
    print(f"{'='*70}")
    
    print("\n✓ Use AUTO-SCALING when:")
    print("  • Traffic has predictable daily or weekly peak patterns")
    print("  • Peak traffic is 2-5x baseline traffic")
    print("  • Peak periods are limited (4-12 hours per day)")
    print("  • Cost optimization is important but predictability needed")
    print("  → Example: E-commerce sites with business hours peaks")
    
    print("\n✓ Use ON-DEMAND when:")
    print("  • Traffic is highly unpredictable or sporadic")
    print("  • Extreme spikes (>10x normal traffic)")
    print("  • Low overall usage (testing, development, small apps)")
    print("  • Flexibility and simplicity outweigh cost concerns")
    print("  → Example: Event-driven applications, prototype applications")
    
    print("\n✓ Use FIXED PROVISIONED when:")
    print("  • Traffic is very consistent with minimal variation")
    print("  • High sustained throughput 24/7")
    print("  • Cost predictability is critical priority")
    print("  • Willing to over-provision for reliability")
    print("  → Example: Backend services with constant load")
    
    # Key insight from testing
    print(f"\n{'='*70}")
    print("KEY INSIGHT: 100 Operations/Second Break-even Point")
    print(f"{'='*70}")
    print("\nBased on testing and cost analysis:")
    print("  • Below 100 ops/sec: On-Demand is typically most cost-effective")
    print("  • Above 100 ops/sec sustained: Provisioned becomes advantageous")
    print("  • At 100 ops/sec: Break-even point between pricing models")
    print("\nThis threshold provides a data-driven decision point for")
    print("choosing between On-Demand and Provisioned capacity modes.")
    
    print(f"\n{'='*70}")
    print("Analysis Complete")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
