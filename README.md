# DynamoDB Cost Optimization for E-commerce

CS6620 Cloud Computing - Team Project

## Project Goal
Reduce DynamoDB costs by 50-70% using Infrastructure as Code (Terraform) for e-commerce Black Friday traffic scenarios.

## Current Progress ✅
- [x] Environment setup (Terraform, AWS CLI, Python)
- [x] Basic Terraform module structure
- [x] DynamoDB module implementation
- [x] Development environment deployed
- [x] GitHub repository setup

## Project Structure
```
dynamodb-cost-optimization/
├── terraform/
│   ├── modules/
│   │   └── dynamodb/          # Reusable DynamoDB module
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   ├── environments/
│   │   └── dev/                # Development environment
│   │       └── main.tf
│   └── backend/                # S3 backend setup
│       └── main.tf
├── scripts/                    # Testing and utility scripts
│   └── README.md
├── docs/                       # Project documentation
│   └── README.md
├── SETUP.md                    # Team setup guide
└── README.md                   # Project overview
```

## Quick Start

### Prerequisites
- Terraform >= 1.0
- AWS CLI configured
- Python 3.x with boto3

### Deploy Development Environment
```bash
cd terraform/environments/dev
terraform init
terraform plan
terraform apply
```

### AWS Resources Created
- DynamoDB Table: `ecommerce-products-dev`
- Billing Mode: PAY_PER_REQUEST (On-Demand)
- Primary Key: `product_id` (String)

## Next Steps
- [ ] Production environment setup
- [ ] Load testing scripts (Python)
- [ ] Cost analysis framework
- [ ] Performance benchmarking
- [ ] Final documentation

## Useful Commands
```bash
# View deployed resources
terraform show

# Destroy resources (cleanup)
terraform destroy

# View outputs
terraform output
```

## Notes
- AWS Learner Lab session expires after 4 hours
- Remember to save work frequently
- Commit changes regularly to GitHub
