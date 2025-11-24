"""
Retry utility module for DynamoDB operations
Implements exponential backoff strategy for handling transient failures
"""

import time
import logging
from botocore.exceptions import ClientError
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries=3, base_delay=1):
    """
    Decorator that implements retry logic with exponential backoff for DynamoDB operations.
    
    This decorator automatically retries failed operations when encountering transient errors
    such as throttling or temporary service unavailability. It uses exponential backoff to
    progressively increase wait time between retries, which helps prevent overwhelming the service.
    
    Args:
        max_retries (int): Maximum number of retry attempts. Default is 3.
        base_delay (float): Initial delay in seconds between retries. Default is 1.
                           Delay doubles with each retry (exponential backoff).
    
    Returns:
        function: Decorated function with retry capability
    
    Example:
        @retry_with_backoff(max_retries=3, base_delay=1)
        def put_item(table, item):
            return table.put_item(Item=item)
    
    Raises:
        ClientError: If the operation fails after all retry attempts
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    # Attempt to execute the function
                    return func(*args, **kwargs)
                    
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    
                    # Define retryable error types
                    # These are temporary errors that may succeed on retry
                    retryable_errors = [
                        'ProvisionedThroughputExceededException',  # Capacity exceeded
                        'ThrottlingException',                      # Request rate too high
                        'RequestLimitExceeded',                     # Too many requests
                        'InternalServerError',                      # AWS internal error
                        'ServiceUnavailable'                        # Service temporarily down
                    ]
                    
                    # Check if error is retryable and we haven't exhausted retries
                    if error_code in retryable_errors and attempt < max_retries:
                        # Calculate delay using exponential backoff: delay = base_delay * 2^attempt
                        delay = base_delay * (2 ** attempt)
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed with error: {error_code}. "
                            f"Retrying in {delay} seconds..."
                        )
                        
                        # Wait before next retry
                        time.sleep(delay)
                    else:
                        # Either non-retryable error or exhausted all retries
                        logger.error(
                            f"Operation failed after {attempt + 1} attempt(s). "
                            f"Error: {error_code} - {e.response['Error']['Message']}"
                        )
                        raise
            
        return wrapper
    return decorator


def retry_with_custom_strategy(retryable_errors, max_retries=3, base_delay=1):
    """
    Advanced retry decorator allowing custom specification of retryable errors.
    
    This provides more control over which errors should trigger retries,
    useful for specific application requirements.
    
    Args:
        retryable_errors (list): List of AWS error codes that should trigger retry
        max_retries (int): Maximum number of retry attempts
        base_delay (float): Initial delay in seconds between retries
    
    Returns:
        function: Decorated function with custom retry capability
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    
                    if error_code in retryable_errors and attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"Retrying after {error_code} (attempt {attempt + 1}/{max_retries + 1})"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"Failed with {error_code} after {attempt + 1} attempts")
                        raise
        return wrapper
    return decorator


if __name__ == "__main__":
    """
    Test the retry decorator with a simulated function
    """
    print("Testing retry_with_backoff decorator...")
    
    # Simulate a function that fails twice then succeeds
    call_count = 0
    
    @retry_with_backoff(max_retries=3, base_delay=0.5)
    def simulated_operation():
        global call_count
        call_count += 1
        print(f"  Attempt #{call_count}")
        
        if call_count < 3:
            # Simulate a retryable error
            error_response = {
                'Error': {
                    'Code': 'ThrottlingException',
                    'Message': 'Rate exceeded'
                }
            }
            raise ClientError(error_response, 'PutItem')
        
        return "Success!"
    
    try:
        result = simulated_operation()
        print(f"\n✓ Operation succeeded: {result}")
        print(f"✓ Total attempts: {call_count}")
    except ClientError as e:
        print(f"\n✗ Operation failed: {e}")
    
    print("\nRetry utility module loaded successfully!")
