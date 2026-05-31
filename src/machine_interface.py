# machine_interface.py
# Simulates the HTTP request a Power Plant Fitness machine
# touchscreen would send to the AWS API Gateway at session end.
# This script demonstrates the inter-module communication pattern
# between the machine interface and the cloud normalization engine.

import requests

# AWS API Gateway endpoint (us-west-1)
API_ENDPOINT = "https://hb4wal32bf.execute-api.us-west-1.amazonaws.com/prod/session/credit"

# Sample session payload — simulates Hannah's workout session
payload = {
    "member_id": "PPF-00142",
    "current_watts": 70,
    "sessions_last_30_days": 20,
    "total_lifetime_sessions": 120
}

response = requests.post(
    API_ENDPOINT,
    json=payload
)

print("Status Code:", response.status_code)
print("Response:")
print(response.json())