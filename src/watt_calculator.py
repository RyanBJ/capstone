# watt_calculator.py
# Power Plant Fitness - Wattage Credit Normalization Engine
# MSIT 5910 Capstone Project - Ryan Bains-Jordan
# University of the People

import sys
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
        raise ValueError("raw_watts cannot be negative.")
    if sessions_last_30_days < 0:
        raise ValueError("sessions_last_30_days cannot be negative.")
    if total_lifetime_sessions < 0:
        raise ValueError("total_lifetime_sessions cannot be negative.")

    # --- Consistency Bonus ---

    # New members receive a full 1.0 bonus for their first 12 lifetime
    # sessions — one complete monthly cycle — giving them time to establish
    # a routine before consistency is factored into their rewards.
    # After session 12, the real consistency measurement begins.
    if total_lifetime_sessions <= target_sessions:
        consistency_bonus = 1.0  # Grace period — full bonus
        grace_period = True
    else:
        consistency_bonus = min(
            sessions_last_30_days / target_sessions, 1.0
        )
        grace_period = False

    # --- Final Calculation ---
    # Base credit is always equal to actual watts generated — never reduced.
    # Consistency bonus adds up to 10% on top of the base credit.
    # Maximum possible multiplier: 1.10 (perfect consistency)
    # Minimum possible multiplier: 1.0  (no sessions in last 30 days,
    #                                    but base credit always guaranteed)
    bonus_multiplier = 1.0 + (consistency_bonus * 0.10)
    normalized_credit = current_watts * bonus_multiplier

    return {
        "current_watts": current_watts,
        "total_lifetime_sessions": total_lifetime_sessions,
        "grace_period": grace_period,
        "sessions_last_30_days": sessions_last_30_days,
        "consistency_bonus": round(consistency_bonus, 4),
        "bonus_multiplier": round(bonus_multiplier, 4),
        "normalized_credit": round(normalized_credit, 2),
        "added_to_balance": math.floor(normalized_credit)
    }

def print_session_summary(member_name, result):
    """
    Print a formatted session summary for a member.

    Parameters:
        member_name (str):  Name of the gym member
        result (dict):      Output from calculate_normalized_credit()
    """
    grace_label = " (Grace Period)" if result['grace_period'] else ""

    print(f"\n{'='*48}")
    print(f"  Member:                  {member_name}")
    print(f"{'='*48}")
    print(f"  Current Watts:           {result['current_watts']} W")
    print(f"  Lifetime Sessions:       {result['total_lifetime_sessions']}{grace_label}")
    print(f"  Sessions (Last 30 Days): {result['sessions_last_30_days']}")
    print(f"  Consistency Bonus:       {result['consistency_bonus']}")
    print(f"  Bonus Multiplier:        {result['bonus_multiplier']}")
    print(f"  {'─'*41}")
    print(f"  Normalized Credit:       {result['normalized_credit']} Wh")
    print(f"  Added To Balance:        {result['added_to_balance']} Wh")
    print(f"{'='*48}")


if __name__ == "__main__":

    print("\nPower Plant Fitness — Wattage Credit Normalization Engine")

    if "--interactive" in sys.argv or "-i" in sys.argv:
        print("Enter your session details below:\n")

        try:
            i_name = input("Member name: ")
            i_current_watts = float(input("Session watts generated: "))
            i_sessions_last_30_days = int(input(
                "Sessions completed in last 30 days (not including this one): "))
            i_total_lifetime_sessions = int(input(
                "Total lifetime sessions (not including this one): "))

            m_result = calculate_normalized_credit(
                current_watts=i_current_watts,
                sessions_last_30_days=i_sessions_last_30_days,
                total_lifetime_sessions=i_total_lifetime_sessions
            )
            print_session_summary(i_name, m_result)

        except ValueError as e:
            print(f"\nInvalid input: {e}")
            print("Please re-run and enter valid values.")

    else:
        print("Running demo scenarios for 7 member profiles...\n")
        print("Tip: Run with --interactive or -i to enter your own session.\n")

        # --- Demo Member Profiles ---
        # Each tuple: (name, current_watts, sessions_last_30_days,
        #              total_lifetime_sessions)

        members = [
            (
                "Alice — New Member",
                80,     # Low watts — just starting out
                2,      # Only been twice this month
                2       # Only 2 lifetime sessions — grace period
            ),
            (
                "Ben — Beginner (High Frequency)",
                90,     # Low-moderate watts
                20,     # 5 days a week — very consistent
                20      # Still in grace period — only 20 lifetime sessions
            ),
            (
                "Carmen — Intermediate",
                150,    # Moderate watts
                12,     # Exactly on target frequency
                48      # 4 months in — past grace period
            ),
            (
                "David — Power User (Low Frequency)",
                280,    # Very high watts
                4,      # Once a week — intense but infrequent
                52      # Over a year in — well past grace period
            ),
            (
                "Elena — Consistent Intermediate",
                160,    # Moderate-high watts
                14,     # Slightly above target frequency
                84      # 7 months in — well past grace period
            ),
            (
                "Hannah — Daily Light Rider",
                70,     # Modest watts — Champs-Élysées level effort
                20,     # Nearly every weekday
                120     # 6 months in — well past grace period
            ),
            (
                "Ivan — Weekly Power Session",
                350,    # High watts — intense single session
                4,      # Once a week
                24      # 6 months in — well past grace period
            ),
        ]

        for m_name, m_watts, m_sessions_30, m_lifetime in members:
            m_result = calculate_normalized_credit(
                current_watts=m_watts,
                sessions_last_30_days=m_sessions_30,
                total_lifetime_sessions=m_lifetime
            )
            print_session_summary(m_name, m_result)

    print("\nDemo complete.")