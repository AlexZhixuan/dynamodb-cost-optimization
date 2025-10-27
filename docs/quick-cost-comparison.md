# Quick DynamoDB Cost Comparison

## Pricing Models

### On-Demand
- Write: $1.25 per million
- Read: $0.25 per million
- No capacity planning
- Pay per request

### Provisioned
- WCU: $0.47/month each
- RCU: $0.09/month each
- Must reserve capacity
- Cheaper if utilized >17%

## Quick Example (100 req/s average)

| Mode | Monthly Cost | Notes |
|------|--------------|-------|
| On-Demand | $78 | Simple, no planning |
| Provisioned | $28 | 64% cheaper! |
| Provisioned + Auto-scaling | $28-93 | Handles spikes |

## Recommendation
Use Provisioned with auto-scaling:
- Base: 50 WCU + 50 RCU ($28/mo)
- Scales to: 500 capacity during spikes
- **Annual savings: $717 (64%)**

## Break-Even
Provisioned is cheaper when utilization > 17%
