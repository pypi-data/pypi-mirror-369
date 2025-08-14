import logging
from datetime import datetime
from functools import wraps

def log_time(message="Function completed in"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logging.info(f"⏳ Starting: {func.__name__}")
            start_time = datetime.now()
            result = await func(*args, **kwargs)
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            logging.info(f"{message} {total_time:.3f} seconds")
            return result
        return wrapper
    return decorator