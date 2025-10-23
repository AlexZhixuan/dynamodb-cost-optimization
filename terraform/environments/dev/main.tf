terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

module "ecommerce_dev_table" {
  source = "../../modules/dynamodb"
  
  table_name   = "ecommerce-products-dev"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "product_id"
  hash_key_type = "S"
  
  tags = {
    Environment = "development"
    Project     = "DynamoDB-Cost-Optimization"
    ManagedBy   = "Terraform"
    Owner       = "Zhixuan"
  }
}

output "dev_table_name" {
  value       = module.ecommerce_dev_table.table_name
  description = "Development table name"
}

output "dev_table_arn" {
  value       = module.ecommerce_dev_table.table_arn
  description = "Development table ARN"
}
