# machine_interface.py
# Simulates the HTTP request a Power Plant Fitness machine
# touchscreen would send to the AWS API Gateway at session end.

# Machine interface sends session data to AWS API Gateway
import requests

payload = {
    "member_id": "PPF-00142",
    "current_watts": 70,
    "sessions_last_30_days": 20,
    "total_lifetime_sessions": 120
}

response = requests.post(
    "https://api.powerplantfitness.com/session/credit",
    json=payload,
    headers={"Authorization": "Bearer <member_token>"}
)

print(response.json())