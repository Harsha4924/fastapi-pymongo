import logging
from time import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logging.basicConfig(
    filename="request_logs.log",
    format="%(asctime)s - %(message)s",
    level=logging.INFO,
)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time()  # Record the start time
        
        response = await call_next(request)  
        
        
        process_time = time() - start_time
        log_message = (
            f"Method: {request.method}, "
            f"Path: {request.url.path}, "
            f"Status Code: {response.status_code}, "
            f"Response Time: {process_time:.3f} seconds, "
            f"Client IP: {request.client.host}"
        )
        
        
        logging.info(log_message)
        
        return response



