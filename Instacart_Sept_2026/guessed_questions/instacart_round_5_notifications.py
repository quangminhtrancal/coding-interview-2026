"""Instacart / CodeSignal, Round 5: implement library notifications.

RECONSTRUCTED QUESTION
Use an AI coding agent to implement the Round 4 notification feature across the
provided project. Include idempotent due-soon/due-now processing, FIFO hold
allocation for N available copies, an in-app notification list, read state, and
full tests.

This standalone Python answer models the business layer. A production service
should enforce the same idempotency keys with database unique constraints and
allocate holds inside a transaction with row locking.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal
import unittest


COMPANY = "Instacart"
PLATFORM = "CodeSignal"
Kind = Literal["due_soon", "due_now", "hold_available"]


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class Loan:
    id: int
    patron_id: int
    due_at: datetime
    returned_at: datetime | None = None


@dataclass(frozen=True)
class Hold:
    id: int
    patron_id: int
    book_id: int
    created_at: datetime


@dataclass
class Notification:
    id: int
    patron_id: int
    kind: Kind
    created_at: datetime
    loan_id: int | None = None
    hold_id: int | None = None
    read: bool = False


class NotificationService:
    def __init__(self, loans: list[Loan] | None = None, holds: list[Hold] | None = None):
        self.loans = loans or []
        self.holds = holds or []
        self.notifications: list[Notification] = []

    def process_due(self, now: datetime) -> list[Notification]:
        now = as_utc(now)
        created = []
        for loan in self.loans:
            if loan.returned_at is not None:
                continue
            due_at = as_utc(loan.due_at)
            if now >= due_at:
                kind: Kind = "due_now"
            elif now >= due_at - timedelta(hours=24):
                kind = "due_soon"
            else:
                continue
            if self._exists(loan_id=loan.id, kind=kind):
                continue
            created.append(self._create(loan.patron_id, kind, now, loan_id=loan.id))
        return created

    def allocate_holds(
        self, book_id: int, available_copies: int, now: datetime
    ) -> list[Notification]:
        if available_copies < 0:
            raise ValueError("available_copies cannot be negative")
        waiting = sorted(
            (hold for hold in self.holds if hold.book_id == book_id),
            key=lambda hold: (as_utc(hold.created_at), hold.id),
        )
        eligible = [
            hold
            for hold in waiting
            if not self._exists(hold_id=hold.id, kind="hold_available")
        ]
        return [
            self._create(
                hold.patron_id,
                "hold_available",
                as_utc(now),
                hold_id=hold.id,
            )
            for hold in eligible[:available_copies]
        ]

    def list_for_patron(self, patron_id: int) -> list[Notification]:
        return sorted(
            (item for item in self.notifications if item.patron_id == patron_id),
            key=lambda item: (item.created_at, item.id),
            reverse=True,
        )

    def mark_read(self, notification_id: int) -> Notification:
        for item in self.notifications:
            if item.id == notification_id:
                item.read = True
                return item
        raise KeyError(notification_id)

    def _exists(
        self,
        *,
        kind: Kind,
        loan_id: int | None = None,
        hold_id: int | None = None,
    ) -> bool:
        return any(
            item.kind == kind and item.loan_id == loan_id and item.hold_id == hold_id
            for item in self.notifications
        )

    def _create(
        self,
        patron_id: int,
        kind: Kind,
        created_at: datetime,
        *,
        loan_id: int | None = None,
        hold_id: int | None = None,
    ) -> Notification:
        item = Notification(
            len(self.notifications) + 1,
            patron_id,
            kind,
            created_at,
            loan_id,
            hold_id,
        )
        self.notifications.append(item)
        return item


class Round5Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 8, 12, tzinfo=timezone.utc)

    def test_due_boundaries_retries_and_returned_loans(self) -> None:
        service = NotificationService(
            loans=[
                Loan(1, 10, self.now + timedelta(hours=24)),
                Loan(2, 20, self.now),
                Loan(3, 30, self.now + timedelta(hours=25)),
                Loan(4, 40, self.now, returned_at=self.now),
            ]
        )
        self.assertEqual(
            [(item.loan_id, item.kind) for item in service.process_due(self.now)],
            [(1, "due_soon"), (2, "due_now")],
        )
        self.assertEqual(service.process_due(self.now), [])
        service.process_due(self.now + timedelta(hours=24))
        self.assertEqual(
            [item.kind for item in service.notifications if item.loan_id == 1],
            ["due_soon", "due_now"],
        )

    def test_holds_are_fifo_limited_and_idempotent(self) -> None:
        service = NotificationService(
            holds=[
                Hold(2, 20, 7, self.now - timedelta(hours=2)),
                Hold(1, 10, 7, self.now - timedelta(hours=2)),
                Hold(3, 30, 7, self.now - timedelta(hours=1)),
            ]
        )
        self.assertEqual(
            [item.hold_id for item in service.allocate_holds(7, 2, self.now)], [1, 2]
        )
        self.assertEqual(
            [item.hold_id for item in service.allocate_holds(7, 2, self.now)], [3]
        )
        self.assertEqual(service.allocate_holds(7, 2, self.now), [])

    def test_list_newest_first_and_mark_read_is_idempotent(self) -> None:
        service = NotificationService(
            loans=[Loan(1, 10, self.now + timedelta(hours=24))],
            holds=[Hold(1, 10, 2, self.now)],
        )
        service.process_due(self.now)
        service.allocate_holds(2, 1, self.now + timedelta(minutes=1))
        listed = service.list_for_patron(10)
        self.assertEqual([item.kind for item in listed], ["hold_available", "due_soon"])
        service.mark_read(listed[0].id)
        service.mark_read(listed[0].id)
        self.assertTrue(listed[0].read)


if __name__ == "__main__":
    unittest.main()
