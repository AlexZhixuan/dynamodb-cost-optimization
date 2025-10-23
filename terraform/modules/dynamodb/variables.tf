variable "table_name" {
  type        = string
  description = "Name of the DynamoDB table"
}

variable "billing_mode" {
  type        = string
  description = "Billing mode: PAY_PER_REQUEST or PROVISIONED"
  default     = "PAY_PER_REQUEST"
}

variable "hash_key" {
  type        = string
  description = "Hash key (partition key) attribute name"
}

variable "hash_key_type" {
  type        = string
  description = "Hash key attribute type (S=String, N=Number, B=Binary)"
  default     = "S"
}

variable "read_capacity" {
  type        = number
  description = "Read capacity units for PROVISIONED mode"
  default     = 5
}

variable "write_capacity" {
  type        = number
  description = "Write capacity units for PROVISIONED mode"
  default     = 5
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to the table"
  default     = {}
}
