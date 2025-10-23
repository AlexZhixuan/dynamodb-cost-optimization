output "table_name" {
  value       = aws_dynamodb_table.this.name
  description = "Name of the DynamoDB table"
}

output "table_arn" {
  value       = aws_dynamodb_table.this.arn
  description = "ARN of the DynamoDB table"
}

output "table_id" {
  value       = aws_dynamodb_table.this.id
  description = "ID of the DynamoDB table"
}
