# test features
import pytest

from recur_scan.features_osasere import (
    get_day_of_month_consistency,
    get_day_of_month_variability,
    get_median_period,
    get_recurrence_confidence,
    has_min_recurrence_period,
    is_weekday_consistent,
)
from recur_scan.transactions import Transaction


def test_has_min_recurrence_period() -> None:
    """Test that has_min_recurrence_period correctly identifies if transactions span min_days."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-15"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-15"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-03-15"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-01-01"),
    ]
    # Netflix spans 60 days (Jan 15 to Mar 15)
    assert has_min_recurrence_period(transactions[0], transactions, min_days=60)
    # Spotify only has one transaction
    assert not has_min_recurrence_period(transactions[3], transactions)


# Osaseres tests
def test_get_day_of_month_consistency() -> None:
    """Test that get_day_of_month_consistency calculates correct fraction of matching dates."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-15"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-15"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-03-16"),  # +1 day
        Transaction(id=4, user_id="user1", name="Netflix", amount=15.99, date="2024-04-10"),  # -5 days
        Transaction(id=5, user_id="user1", name="Amazon", amount=12.99, date="2024-01-31"),
        Transaction(id=6, user_id="user1", name="Amazon", amount=12.99, date="2024-02-28"),
    ]
    # Netflix: 3/4 transactions within ±1 day of 15th
    assert get_day_of_month_consistency(transactions[0], transactions, tolerance_days=1) == 0.75
    # Amazon: both transactions treated as month-end
    assert get_day_of_month_consistency(transactions[4], transactions, tolerance_days=3) == 1.0


def test_get_day_of_month_variability() -> None:
    """Test that get_day_of_month_variability calculates correct standard deviation."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Consistent", amount=10.00, date="2024-01-15"),
        Transaction(id=2, user_id="user1", name="Consistent", amount=10.00, date="2024-02-15"),
        Transaction(id=3, user_id="user1", name="Variable", amount=10.00, date="2024-01-05"),
        Transaction(id=4, user_id="user1", name="Variable", amount=10.00, date="2024-02-20"),
        Transaction(id=5, user_id="user1", name="MonthEnd", amount=10.00, date="2024-01-31"),
        Transaction(id=6, user_id="user1", name="MonthEnd", amount=10.00, date="2024-02-28"),
    ]
    # Consistent dates should have low variability
    assert get_day_of_month_variability(transactions[0], transactions) < 1.0
    # Variable dates should have higher variability
    assert get_day_of_month_variability(transactions[2], transactions) > 7.0
    # Month-end dates should be treated as similar
    assert get_day_of_month_variability(transactions[4], transactions) < 3.0


def test_get_recurrence_confidence() -> None:
    """Test that get_recurrence_confidence calculates correct weighted confidence score."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Regular", amount=10.00, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Regular", amount=10.00, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Regular", amount=10.00, date="2024-03-01"),
        Transaction(id=4, user_id="user1", name="Irregular", amount=10.00, date="2024-01-01"),
        Transaction(id=5, user_id="user1", name="Irregular", amount=10.00, date="2024-01-15"),
        Transaction(id=6, user_id="user1", name="Irregular", amount=10.00, date="2024-03-20"),
    ]
    # Regular monthly transactions should have high confidence
    assert get_recurrence_confidence(transactions[0], transactions) > 0.7
    # Irregular transactions should have low confidence
    assert get_recurrence_confidence(transactions[3], transactions) < 0.5


def test_is_weekday_consistent() -> None:
    """Test that is_weekday_consistent correctly identifies consistent weekdays."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Weekly", amount=5.00, date="2024-01-01"),  # Monday
        Transaction(id=2, user_id="user1", name="Weekly", amount=5.00, date="2024-01-08"),  # Monday
        Transaction(id=3, user_id="user1", name="Biweekly", amount=10.00, date="2024-01-01"),  # Monday
        Transaction(id=4, user_id="user1", name="Biweekly", amount=10.00, date="2024-01-15"),  # Monday
        Transaction(id=5, user_id="user1", name="Random", amount=15.00, date="2024-01-01"),  # Monday
        Transaction(id=6, user_id="user1", name="Random", amount=15.00, date="2024-01-03"),  # Wednesday
        Transaction(id=7, user_id="user1", name="Random", amount=15.00, date="2024-01-07"),  # Sunday
    ]
    # Consistent weekday (all Mondays)
    assert is_weekday_consistent(transactions[0], transactions)
    # Also consistent (only 2 weekdays)
    assert is_weekday_consistent(transactions[2], transactions)
    # Inconsistent (3 different weekdays)
    assert not is_weekday_consistent(transactions[4], transactions)


def test_get_median_period() -> None:
    """Test that get_median_period calculates correct median days between transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Monthly", amount=10.00, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Monthly", amount=10.00, date="2024-02-01"),  # 31 days
        Transaction(id=3, user_id="user1", name="Monthly", amount=10.00, date="2024-03-01"),  # 29 days
        Transaction(id=4, user_id="user1", name="Biweekly", amount=5.00, date="2024-01-01"),
        Transaction(id=5, user_id="user1", name="Biweekly", amount=5.00, date="2024-01-15"),  # 14 days
        Transaction(id=6, user_id="user1", name="Biweekly", amount=5.00, date="2024-01-29"),  # 14 days
        Transaction(id=7, user_id="user1", name="Single", amount=20.00, date="2024-01-01"),
    ]
    # Monthly transactions median should be ~30 days
    assert get_median_period(transactions[0], transactions) == pytest.approx(30.0, abs=1.0)
    # Biweekly transactions median should be 14 days
    assert get_median_period(transactions[3], transactions) == 14.0
    # Single transaction should return 0
    assert get_median_period(transactions[6], transactions) == 0.0
