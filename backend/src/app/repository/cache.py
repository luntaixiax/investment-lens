import os
from yokedcache import YokedCache

# Use environment variable for Redis host, defaulting to localhost for local development
# In Docker, set REDIS_HOST=cache
redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_url = f"redis://{redis_host}:6379"

cache = YokedCache(redis_url=redis_url)
