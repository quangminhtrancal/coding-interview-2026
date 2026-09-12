"""Instacart / CodeSignal, Round 3: debug backend metrics filtering.

RECONSTRUCTED QUESTION
A value on the metrics page is incorrect. Find and fix the bug. The public report
says the defect was in the Python backend: results were returned/aggregated before
the records were correctly filtered, so the fix changed the operation order.

The exact metric and schema were not disclosed. This representative answer
calculates loan metrics after applying an inclusive creation-date filter.
"""

from dataclasses import dataclass
from datetime import date, datetime, timezone
import unittest


COMPANY = "Instacart"
PLATFORM = "CodeSignal"


@dataclass(frozen=True)
class Loan:
    created_at: datetime
    due_at: datetime
    returned_at: datetime | None = None


def loan_metrics(
    loans: list[Loan], from_date: date, to_date: date, now: datetime
) -> dict[str, int]:
    """Filter first, then aggregate only records inside the inclusive range."""
    if from_date > to_date:
        raise ValueError("from_date must not be after to_date")

    filtered = [
        loan for loan in loans if from_date <= loan.created_at.date() <= to_date
    ]
    return {
        "total": len(filtered),
        "returned": sum(loan.returned_at is not None for loan in filtered),
        "overdue": sum(
            loan.returned_at is None and loan.due_at < now for loan in filtered
        ),
    }


class Round3Tests(unittest.TestCase):
    def test_filter_happens_before_aggregation_and_boundaries_are_inclusive(self) -> None:
        utc = timezone.utc
        now = datetime(2026, 10, 1, tzinfo=utc)
        loans = [
            Loan(datetime(2026, 9, 1, tzinfo=utc), datetime(2026, 10, 2, tzinfo=utc)),
            Loan(datetime(2026, 9, 30, 23, tzinfo=utc), datetime(2026, 9, 29, tzinfo=utc)),
            Loan(
                datetime(2026, 8, 31, tzinfo=utc),
                datetime(2026, 9, 1, tzinfo=utc),
                returned_at=datetime(2026, 9, 1, tzinfo=utc),
            ),
        ]
        self.assertEqual(
            loan_metrics(loans, date(2026, 9, 1), date(2026, 9, 30), now),
            {"total": 2, "returned": 0, "overdue": 1},
        )

    def test_empty_and_invalid_ranges(self) -> None:
        utc = timezone.utc
        now = datetime(2026, 9, 1, tzinfo=utc)
        self.assertEqual(
            loan_metrics([], date(2026, 9, 1), date(2026, 9, 30), now),
            {"total": 0, "returned": 0, "overdue": 0},
        )
        with self.assertRaises(ValueError):
            loan_metrics([], date(2026, 9, 2), date(2026, 9, 1), now)


if __name__ == "__main__":
    unittest.main()
