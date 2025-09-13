import os
import redis

# Use environment variables for flexibility. This allows you to easily switch
# between 'localhost' for local testing and a static IP for GCP.
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Create a single, reusable Redis client connection.
# decode_responses=True ensures that data read from Redis is in a human-readable string format.
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

print(f"Redis client configured for {REDIS_HOST}:{REDIS_PORT}")
