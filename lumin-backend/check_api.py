import requests
import os
import sys

# Setup Django standalone to use internal models if needed (optional, but requests is simpler)
# We will just use requests to hit the running server

session_cookie = None
# If we could get a session cookie, we would use it. 
# But let's try to hit the endpoint and see if we get 403 (meaning reachable but auth required)
# or connection error (meaning server not running/reachable)

url = "http://127.0.0.1:8000/api/products/data/products/"

try:
    print(f"Connecting to {url}...")
    response = requests.get(url, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    if response.status_code == 200:
        print("Success! Data preview:")
        print(str(response.json())[:200])
    elif response.status_code == 403:
        print("403 Forbidden - Endpoint reachable but requires auth (Expected if no cookie).")
        # Checking if it returns JSON or HTML
        print("Content Type:", response.headers.get('content-type'))
    else:
        print("Error content:")
        print(response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("FATAL: Could not connect to localhost:8000. Is the server running?")
except Exception as e:
    print(f"An error occurred: {e}")
