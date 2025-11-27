terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "terraform-state-dynamodb-zhixuan"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

# Production DynamoDB Table with Provisioned Capacity
module "ecommerce_prod_table" {
  source = "../../modules/dynamodb"
  
  table_name     = "ecommerce-products-prod"
  billing_mode   = "PROVISIONED"
  hash_key       = "product_id"
  hash_key_type  = "S"
  
  # Based on Shuang's cost analysis: 100 ops/sec threshold
  read_capacity  = 100
  write_capacity = 100
  
  tags = {
    Environment = "production"
    Project     = "DynamoDB-Cost-Optimization"
    ManagedBy   = "Terraform"
    Owner       = "Zhixuan"
    CostCenter  = "Infrastructure"
  }
}

# Auto-scaling for Read Capacity
resource "aws_appautoscaling_target" "dynamodb_table_read_target" {
  max_capacity       = 1000
  min_capacity       = 100
  resource_id        = "table/${module.ecommerce_prod_table.table_name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "dynamodb_table_read_policy" {
  name               = "DynamoDBReadCapacityUtilization:${module.ecommerce_prod_table.table_name}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dynamodb_table_read_target.resource_id
  scalable_dimension = aws_appautoscaling_target.dynamodb_table_read_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dynamodb_table_read_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
    target_value = 70.0
  }
}

# Auto-scaling for Write Capacity
resource "aws_appautoscaling_target" "dynamodb_table_write_target" {
  max_capacity       = 1000
  min_capacity       = 100
  resource_id        = "table/${module.ecommerce_prod_table.table_name}"
  scalable_dimension = "dynamodb:table:WriteCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "dynamodb_table_write_policy" {
  name               = "DynamoDBWriteCapacityUtilization:${module.ecommerce_prod_table.table_name}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dynamodb_table_write_target.resource_id
  scalable_dimension = aws_appautoscaling_target.dynamodb_table_write_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dynamodb_table_write_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }
    target_value = 70.0
  }
}

# Outputs
output "prod_table_name" {
  value       = module.ecommerce_prod_table.table_name
  description = "Production table name"
}

output "prod_table_arn" {
  value       = module.ecommerce_prod_table.table_arn
  description = "Production table ARN"
}

output "autoscaling_read_target" {
  value       = aws_appautoscaling_target.dynamodb_table_read_target.id
  description = "Read capacity auto-scaling target ID"
}

output "autoscaling_write_target" {
  value       = aws_appautoscaling_target.dynamodb_table_write_target.id
  description = "Write capacity auto-scaling target ID"
}
