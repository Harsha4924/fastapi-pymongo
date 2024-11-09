
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from time import time


RATE_LIMIT = 10  
TIME_WINDOW = 60 


user_requests = {}

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time()
        

        if client_ip not in user_requests:
            user_requests[client_ip] = []
        
        
        user_requests[client_ip] = [
            timestamp for timestamp in user_requests[client_ip]
            if current_time - timestamp < TIME_WINDOW
        ]
        
        
        if len(user_requests[client_ip]) >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
        
       
        user_requests[client_ip].append(current_time)
        
        response = await call_next(request)
        return response

