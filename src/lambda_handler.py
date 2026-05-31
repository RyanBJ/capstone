# lambda_handler.py
# Power Plant Fitness - AWS Lambda Handler
# Conceptual version showing integration with watt_calculator module.
# For the self-contained deployment version, see lambda_function.py

import json
from watt_calculator import calculate_normalized_credit

def lambda_handler(event, context):
    try:
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
    except KeyError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Missing field: {str(e)}"})
        }