# Manual DynamoDB Table Creation - Member A

## Date: [Today's date]
## Completed by: Sam (Member A)

## Objective
Create a DynamoDB table manually in AWS Console to understand the service before automating with Terraform.

## Steps Completed

### 1. Table Configuration
- **Table name:** products-demo
- **Partition key:** product_id (String)
- **Billing mode:** On-Demand (PAY_PER_REQUEST)
- **Region:** [Your region - likely us-east-1 or us-west-2]

### 2. Test Data Added
Created 5 sample product items:

1. **PROD-001** - Laptop ($999.99, stock: 50)
2. **PROD-002** - Mouse ($29.99, stock: 200)
3. **PROD-003** - Keyboard ($79.99, stock: 150)
4. **PROD-004** - Monitor ($299.99, stock: 75)
5. **PROD-005** - Webcam ($89.99, stock: 120)

### 3. Screenshots Captured
- ✅ Screenshot 1: Table metrics/overview
- ✅ Screenshot 2: All 5 items displayed
