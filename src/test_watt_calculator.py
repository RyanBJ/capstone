# test_watt_calculator.py
# Power Plant Fitness - Unit Tests for Wattage Credit Normalization Engine
# MSIT 5910 Capstone Project - Ryan Bains-Jordan

import pytest
from watt_calculator import calculate_normalized_credit


class TestGracePeriod:
    """Tests for new member grace period behavior."""

    def test_new_member_receives_full_bonus(self):
        """New member with 0 lifetime sessions should receive full 1.0 consistency bonus."""
        result = calculate_normalized_credit(
            current_watts=80,
            sessions_last_30_days=0,
            total_lifetime_sessions=0
        )
        assert result["consistency_bonus"] == 1.0
        assert result["grace_period"] is True

    def test_grace_period_active_at_session_12(self):
        """Member with exactly 12 lifetime sessions should still be in grace period."""
        result = calculate_normalized_credit(
            current_watts=100,
            sessions_last_30_days=12,
            total_lifetime_sessions=12
        )
        assert result["grace_period"] is True
        assert result["consistency_bonus"] == 1.0

    def test_grace_period_ends_at_session_13(self):
        """Member with 13 lifetime sessions should be past grace period."""
        result = calculate_normalized_credit(
            current_watts=100,
            sessions_last_30_days=4,
            total_lifetime_sessions=13
        )
        assert result["grace_period"] is False


class TestConsistencyBonus:
    """Tests for consistency bonus calculation."""

    def test_full_bonus_at_target_sessions(self):
        """Member hitting exactly 12 sessions should receive full 1.0 bonus."""
        result = calculate_normalized_credit(
            current_watts=150,
            sessions_last_30_days=12,
            total_lifetime_sessions=48
        )
        assert result["consistency_bonus"] == 1.0

    def test_bonus_capped_above_target(self):
        """Member exceeding 12 sessions should be capped at 1.0."""
        result = calculate_normalized_credit(
            current_watts=150,
            sessions_last_30_days=20,
            total_lifetime_sessions=120
        )
        assert result["consistency_bonus"] == 1.0

    def test_partial_bonus_below_target(self):
        """Member with 4 sessions should receive 0.333 consistency bonus."""
        result = calculate_normalized_credit(
            current_watts=280,
            sessions_last_30_days=4,
            total_lifetime_sessions=52
        )
        assert result["consistency_bonus"] == pytest.approx(0.3333, abs=0.001)

    def test_zero_sessions_outside_grace(self):
        """Member with 0 sessions in last 30 days outside grace period."""
        result = calculate_normalized_credit(
            current_watts=100,
            sessions_last_30_days=0,
            total_lifetime_sessions=50
        )
        assert result["consistency_bonus"] == 0.0


class TestBaseCredit:
    """Tests ensuring base credit always equals actual watts generated."""

    def test_base_credit_guaranteed(self):
        """Member should always earn at least their raw wattage."""
        result = calculate_normalized_credit(
            current_watts=62,
            sessions_last_30_days=0,
            total_lifetime_sessions=50
        )
        assert result["added_to_balance"] >= 62

    def test_maximum_bonus_multiplier(self):
        """Perfect consistency should produce exactly 1.25 multiplier."""
        result = calculate_normalized_credit(
            current_watts=100,
            sessions_last_30_days=12,
            total_lifetime_sessions=48
        )
        assert result["bonus_multiplier"] == pytest.approx(1.25, abs=0.001)

    def test_minimum_bonus_multiplier(self):
        """Zero consistency outside grace period should produce exactly 1.0 multiplier."""
        result = calculate_normalized_credit(
            current_watts=100,
            sessions_last_30_days=0,
            total_lifetime_sessions=50
        )
        assert result["bonus_multiplier"] == pytest.approx(1.0, abs=0.001)


class TestInputValidation:
    """Tests for input validation and error handling."""

    def test_negative_watts_raises_error(self):
        """Negative wattage should raise ValueError."""
        with pytest.raises(ValueError, match="current_watts cannot be negative"):
            calculate_normalized_credit(
                current_watts=-10,
                sessions_last_30_days=5,
                total_lifetime_sessions=20
            )

    def test_negative_sessions_raises_error(self):
        """Negative sessions should raise ValueError."""
        with pytest.raises(ValueError, match="sessions_last_30_days cannot be negative"):
            calculate_normalized_credit(
                current_watts=100,
                sessions_last_30_days=-1,
                total_lifetime_sessions=20
            )

    def test_negative_lifetime_sessions_raises_error(self):
        """Negative lifetime sessions should raise ValueError."""
        with pytest.raises(ValueError, match="total_lifetime_sessions cannot be negative"):
            calculate_normalized_credit(
                current_watts=100,
                sessions_last_30_days=5,
                total_lifetime_sessions=-1
            )

    def test_zero_watts_valid(self):
        """Zero watts should be valid — member logged in but generated nothing."""
        result = calculate_normalized_credit(
            current_watts=0,
            sessions_last_30_days=5,
            total_lifetime_sessions=20
        )
        assert result["normalized_credit"] == 0.0
        assert result["added_to_balance"] == 0


class TestHannahIvanComparison:
    """Validates the core fairness narrative of the system."""

    def test_consistent_member_outearns_infrequent_per_month(self):
        """
        Hannah (20 sessions, 70W) should outearn Ivan (4 sessions, 350W)
        on a monthly basis despite 5x lower per-session wattage.
        """
        hannah_result = calculate_normalized_credit(
            current_watts=70,
            sessions_last_30_days=20,
            total_lifetime_sessions=120
        )
        ivan_result = calculate_normalized_credit(
            current_watts=350,
            sessions_last_30_days=4,
            total_lifetime_sessions=24
        )

        hannah_monthly = hannah_result["normalized_credit"] * 20
        ivan_monthly = ivan_result["normalized_credit"] * 4

        assert hannah_monthly > ivan_monthly