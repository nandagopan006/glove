import logging
import time
import uuid

# Get the project logger
logger = logging.getLogger('project')

class RequestLoggingMiddleware:
    """
    Middleware to log every request and response with a unique request ID.
    Useful for tracking the flow of a single request across logs.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate a unique request ID 
        request.request_id = str(uuid.uuid4())
        
        start_time = time.time()
        
        # Extract user info for logging
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        
       
        # We use 'info' for general flow, but you could use 'debug' to reduce noise
        logger.info(f"START REQUEST [{request.request_id}] {request.method} {request.path} - User: {user}")

        # Process the request
        response = self.get_response(request)
        
        
        duration = time.time() - start_time
        
     
        # Using different levels based on status code
        log_msg = f"END REQUEST [{request.request_id}] Status: {response.status_code} - Duration: {duration:.3f}s"
        
        if response.status_code >= 500:
            logger.error(log_msg)
        elif response.status_code >= 400:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        # 
        response['X-Request-ID'] = request.request_id
        
        return response
