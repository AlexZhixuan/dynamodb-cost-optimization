# Scripts Directory

This directory contains testing and utility scripts for the DynamoDB cost optimization project.

## Testing Scripts (`/testing`)

### Completed Scripts
- `test_connection.py` - Tests AWS DynamoDB connectivity and lists tables
- `crud_operations.py` - Complete CRUD (Create, Read, Update, Delete) operations testing
- `simple_load_test.py` - Load testing script for performance evaluation
- `cost_calculator.py` - Cost comparison tool for On-Demand vs Provisioned pricing
- `test_results.md` - Documentation of test results and findings

### Setup
1. Install requirements: `pip install -r testing/requirements.txt`
2. Configure AWS credentials in `.env` file
3. Ensure DynamoDB table exists (e.g., `products-demo`)

### Usage Examples
```bash
# Test connection
python scripts/testing/test_connection.py

# Run CRUD operations
python scripts/testing/crud_operations.py

# Perform load test
python scripts/testing/simple_load_test.py

# Calculate costs
python scripts/testing/cost_calculator.py
```

## Test Results
- Connection: Successful
- CRUD Operations: 100% success rate
- Load Test: 37.1% success rate at 5 ops/sec
- Cost Analysis: Break-even at ~100 ops/sec continuous

## Future Improvements
- Add retry logic for failed operations
- Implement more sophisticated load patterns
- Add data validation tests
