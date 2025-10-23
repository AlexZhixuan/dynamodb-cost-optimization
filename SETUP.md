# Team Setup Guide

## For Team Members (Jing & Shuang)

### 1. Clone Repository
```bash
git clone https://github.com/AlexZhixuan/dynamodb-cost-optimization.git
cd dynamodb-cost-optimization
```

### 2. Install Prerequisites
- Install Terraform: https://www.terraform.io/downloads
- Install AWS CLI: https://aws.amazon.com/cli/
- Install Python 3 and boto3: `pip3 install boto3`

### ⚠️3. Configure AWS Credentials (会变）
1. Start AWS Learner Lab
2. Click "AWS Details" → "Show"
3. Copy credentials to `~/.aws/credentials`:
```
```

### 4. Work with Terraform
```bash
cd terraform/environments/dev
terraform init     # Initialize (downloads providers, connects to S3 backend)
terraform plan     # Preview changes
terraform apply    # Apply changes
terraform destroy  # Clean up resources
```

## Important Notes
- ⚠️ Credentials change every time you restart Lab
- ⚠️ Always `git pull` before making changes
- ⚠️ Always `git push` after making changes
- ⚠️ Terraform state is stored in S3: `terraform-state-dynamodb-zhixuan`

## Current Resources
- DynamoDB Table: `ecommerce-products-dev`
- S3 Bucket: `terraform-state-dynamodb-zhixuan`
