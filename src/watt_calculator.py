# watt_calculator.py
# Power Plant Fitness - Wattage Credit Normalization Engine
# MSIT 5910 Capstone Project - Ryan Bains-Jordan
# University of the People

import sys
import math

def calculate_normalized_credit(
        raw_watts,
        duration_seconds,
        resistance_level,
        baseline_watts,
        sessions_last_30_days,
        target_sessions=12):
    """
    Calculate a normalized wattage credit for a member's workout session.
    
    Parameters:
        raw_watts (float):              Average wattage generated during session
        duration_seconds (int):         Total session duration in seconds
        resistance_level (int):         Machine resistance setting (1-10)
        baseline_watts (float):         Member's historical average wattage output over the last 90 days
        sessions_last_30_days (int):    Number of sessions completed in the last 30 days
        target_sessions (int):          Target sessions per month (default: 12)
    
    Returns:
        dict: Breakdown of all factors and the final normalized wattage credit (Wh)
    """

    # --- Input Validation ---
    if raw_watts < 0:
        raise ValueError("raw_watts cannot be negative.")
    if duration_seconds < 0:
        raise ValueError("duration_seconds cannot be negative.")
    if not 1 <= resistance_level <= 10:
        raise ValueError("resistance_level must be between 1 and 10.")
    if baseline_watts < 0:
        raise ValueError("baseline_watts cannot be negative.")
    if sessions_last_30_days < 0:
        raise ValueError("sessions_last_30_days cannot be negative.")

    # --- Factor Calculations ---

    # Step 1: Duration Factor
    # Rewards longer sessions up to a 60 minute
    # A 30-minute session scores 0.5; a 60-minute session scores 1.0
    duration_minutes = duration_seconds / 60
    duration_factor = min(duration_minutes / 60, 1.0)

    # Step 2: Resistance Factor
    # Rewards higher resistance settings on a 1-10 scale
    # Resistance 5 scores 0.5; Resistance 10 scores 1.0
    resistance_factor = resistance_level / 10

    # Step 3: Baseline Factor
    # Rewards effort relative to the member's own historical average over the past 90 days
    # Capped at 1.5 to prevent extreme outliers from distorting credits
    # New members (baseline = 0) receive a neutral factor of 1.0
    if baseline_watts == 0:
        baseline_factor = 1.0  # New member — no history yet, neutral
    else:
        baseline_factor = min(raw_watts / baseline_watts, 1.5)

    # Step 4: Consistency Factor
    # Rewards members who attend regularly over the past 30 days
    # Capped at 1.2 — consistent members earn a maximum 20% bonus
    # New members (0 sessions) receive a neutral factor of 1.0
    if sessions_last_30_days == 0:
        consistency_factor = 1.0  # New member — no history yet, neutral
    else:
        consistency_factor = min(
            sessions_last_30_days / target_sessions, 1.2
        )

    # --- Final Calculation ---
    # Normalized credit = raw output adjusted by all four behavioral factors
    normalized_credit = (
        raw_watts
        * duration_factor
        * resistance_factor
        * baseline_factor
        * consistency_factor
    )

    return {
        "raw_watts": raw_watts,
        "duration_factor": round(duration_factor, 4),
        "resistance_factor": round(resistance_factor, 4),
        "baseline_factor": round(baseline_factor, 4),
        "consistency_factor": round(consistency_factor, 4),
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
    print(f"\n{'='*45}")
    print(f"  Member: {member_name}")
    print(f"{'='*45}")
    print(f"  Raw Watts:            {result['raw_watts']} W")
    print(f"  Duration Factor:      {result['duration_factor']}")
    print(f"  Resistance Factor:    {result['resistance_factor']}")
    print(f"  Baseline Factor:      {result['baseline_factor']}")
    print(f"  Consistency Factor:   {result['consistency_factor']}")
    print(f"  {'─'*38}")
    print(f"  Normalized Credit:    {result['normalized_credit']} Wh")
    print(f"  Added To Balance:     {result['added_to_balance']} Wh")
    print(f"{'='*45}")


if __name__ == "__main__":

    print("\nPower Plant Fitness — Wattage Credit Normalization Engine")

    if "--interactive" in sys.argv or "-i" in sys.argv:
        print("Enter your session details below:\n")

        try:
            i_name = input("Member name: ")
            i_raw_watts = float(input("Session wattage generated: "))
            i_duration_minutes = float(input("Session duration (minutes): "))
            i_resistance_level = int(input("Resistance level (1-10): "))
            i_baseline_watts = float(input("Total number of watts over the last 90 days (0 if new): "))
            i_sessions_last_30_days = int(input("Sessions in last 30 days: "))

            m_result = calculate_normalized_credit(
                raw_watts=i_raw_watts,
                duration_seconds=int(i_duration_minutes * 60),
                resistance_level=i_resistance_level,
                baseline_watts=i_baseline_watts,
                sessions_last_30_days=i_sessions_last_30_days
            )
            print_session_summary(i_name, m_result)

        except ValueError as e:
            print(f"\nInvalid input: {e}")
            print("Please re-run and enter valid values.")

    else:
        print("Running demo scenarios for 7 member profiles...")

        # --- Demo Member Profiles ---
        # Each tuple: (name, raw_watts, duration_seconds, resistance_level,
        #              baseline_watts, sessions_last_30_days)

        members = [
            (
                "Alice — New Member",
                80,         # Low raw watts, just starting out
                1800,       # 30 minutes
                3,          # Low resistance
                0,          # No baseline yet
                0           # No sessions yet
            ),
            (
                "Ben — Beginner (High Frequency)",
                90,         # Low-moderate watts
                1500,       # 25 minutes — shorter sessions
                3,          # Low resistance
                85,         # Low baseline, slightly below today
                20          # 5 days a week — very consistent
            ),
            (
                "Carmen — Intermediate",
                150,        # Moderate watts
                2700,       # 45 minutes
                5,          # Mid-resistance
                140,        # Baseline just below today — improving
                12          # Exactly on target frequency
            ),
            (
                "David — Power User (Low Frequency)",
                280,        # Very high watts
                5400,       # 90 minutes — capped at 60 for factor
                10,         # Maximum resistance
                260,        # High baseline, performing above it
                4           # Once a week — intense but infrequent
            ),
            (
                "Elena — Consistent Intermediate",
                160,        # Moderate-high watts
                3600,       # 60 minutes — full session
                6,          # Moderate-high resistance
                170,        # Slightly below baseline today
                14          # Slightly above target frequency
            ),
            (
                "Frank — Returning Member",
                120,        # Moderate watts
                2400,       # 40 minutes
                5,          # Mid-resistance
                200,        # High baseline — underperforming today
                3           # Just returned after a break
            ),
            (
                "Grace — Elite Member",
                250,        # High watts
                3600,       # 60 minutes
                9,          # Near maximum resistance
                230,        # High baseline, performing above it
                16          # Above target — very consistent
            ),
        ]

        for m_name, m_watts, m_duration, m_resistance, \
                m_baseline, m_sessions in members:
            m_result = calculate_normalized_credit(
                raw_watts=m_watts,
                duration_seconds=m_duration,
                resistance_level=m_resistance,
                baseline_watts=m_baseline,
                sessions_last_30_days=m_sessions
            )
            print_session_summary(m_name, m_result)

    print("\nDemo complete.")