# lambda_function.py
# Power Plant Fitness - Wattage Credit Normalization Engine
# AWS Lambda Handler - Self-contained deployment version
# MSIT 5910 Capstone Project - Ryan Bains-Jordan

import json
import math


def calculate_normalized_credit(
        current_watts,
        sessions_last_30_days,
        total_lifetime_sessions,
        target_sessions=12):
    """
    Calculate a normalized wattage credit for a member's workout session.

    The normalization engine rewards consistency (the number of sessions
    completed in the last 30 days) as the sole behavioral modifier.
    Raw wattage is always guaranteed as the base credit, ensuring no member
    is penalized for their fitness level. New members receive a grace period
    for their first 12 lifetime sessions, after which consistency is measured.

    Parameters:
        current_watts (float):          Wattage generated during this session
        sessions_last_30_days (int):    Sessions completed in the last 30 days
                                        (not including the current session)
        total_lifetime_sessions (int):  Total number of sessions across all time
                                        (not including the current session)
        target_sessions (int):          Target sessions per month (default: 12)

    Returns:
        dict: Breakdown of consistency bonus and final normalized credit (Wh)
    """

    # --- Input Validation ---
    if current_watts < 0:
        raise ValueError("current_watts cannot be negative.")
    if sessions_last_30_days < 0:
        raise ValueError("sessions_last_30_days cannot be negative.")
    if total_lifetime_sessions < 0:
        raise ValueError("total_lifetime_sessions cannot be negative.")

    # --- Consistency Bonus ---
    # New members receive a full 1.0 bonus for their first 12 lifetime
    # sessions — one complete monthly cycle (giving them time to establish
    # a routine before consistency is factored into their rewards).
    if total_lifetime_sessions <= target_sessions:
        consistency_bonus = 1.0
        grace_period = True
    else:
        consistency_bonus = min(
            sessions_last_30_days / target_sessions, 1.0
        )
        grace_period = False

    # --- Final Calculation ---
    # Base credit is always equal to actual watts generated (never reduced).
    # Consistency bonus adds up to 25% on top of the base credit.
    # Maximum possible multiplier: 1.25 (perfect consistency)
    # Minimum possible multiplier: 1.0 (no sessions, base credit guaranteed)
    bonus_multiplier = 1.0 + (consistency_bonus * 0.25)
    normalized_credit = current_watts * bonus_multiplier

    return {
        "current_watts":            current_watts,
        "total_lifetime_sessions":  total_lifetime_sessions,
        "grace_period":             grace_period,
        "sessions_last_30_days":    sessions_last_30_days,
        "consistency_bonus":        round(consistency_bonus, 4),
        "bonus_multiplier":         round(bonus_multiplier, 4),
        "normalized_credit":        round(normalized_credit, 2),
        "added_to_balance":         math.floor(normalized_credit)
    }


def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    Receives session data from API Gateway and returns Watt Wallet credits.
    """

    try:
        # Parse the request body
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        elif isinstance(event.get("body"), dict):
            body = event["body"]
        else:
            body = event  # Direct Lambda test invocation

        # Extract parameters
        current_watts = float(body["current_watts"])
        sessions_last_30_days = int(body["sessions_last_30_days"])
        total_lifetime_sessions = int(body["total_lifetime_sessions"])
        member_id = body.get("member_id", "UNKNOWN")

        # Run normalization
        result = calculate_normalized_credit(
            current_watts=current_watts,
            sessions_last_30_days=sessions_last_30_days,
            total_lifetime_sessions=total_lifetime_sessions
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "member_id": member_id,
                "current_watts": result["current_watts"],
                "consistency_bonus": result["consistency_bonus"],
                "bonus_multiplier": result["bonus_multiplier"],
                "normalized_credit": result["normalized_credit"],
                "added_to_balance": result["added_to_balance"],
                "grace_period": result["grace_period"]
            })
        }

    except KeyError as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": f"Missing required field: {str(e)}"
            })
        }

    except ValueError as e:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": str(e)
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Internal server error",
                "detail": str(e)
            })
        }