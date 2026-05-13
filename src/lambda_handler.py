# lambda_handler.py
# AWS Lambda function that receives machine session data,
# runs the normalization algorithm, and returns Watt Wallet credits.

# AWS Lambda handler — wraps watt_calculator logic
import json
from watt_calculator import calculate_normalized_credit


def lambda_handler(event, context):
    body = json.loads(event["body"])

    result = calculate_normalized_credit(
        current_watts=body["current_watts"],
        sessions_last_30_days=body["sessions_last_30_days"],
        total_lifetime_sessions=body["total_lifetime_sessions"]
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "member_id": body["member_id"],
            "normalized_credit": result["normalized_credit"],
            "added_to_balance": result["added_to_balance"],
            "bonus_multiplier": result["bonus_multiplier"]
        })
    }