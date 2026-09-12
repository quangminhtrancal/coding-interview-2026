"""Instacart / CodeSignal, Round 4: notification requirement discovery.

RECONSTRUCTED QUESTION
Talk to an AI PM to define a library notification feature spanning frontend and
backend. Patrons need notifications 24 hours before an item is due, when it is
due, and when a held item becomes available. If N copies return, notify the first
N patrons in FIFO order. The solution must be idempotent and fully tested.
"""

import unittest


COMPANY = "Instacart"
PLATFORM = "CodeSignal"

CLARIFYING_QUESTIONS = (
    "Are due times stored and compared in UTC, and how are local times displayed?",
    "Does exactly 24 hours before due qualify, and what happens after scheduler delay?",
    "Should a returned loan suppress any pending due notification?",
    "What fields form the idempotency key for each notification type?",
    "Is FIFO ordered by hold creation time, with ID as a deterministic tie-breaker?",
    "Does one available copy notify one waiting hold, and are notified holds skipped?",
    "Can one patron place multiple active holds for the same title?",
    "What transaction or locking protects allocation from concurrent returns?",
    "Are notifications in-app only, and do they have unread/read state?",
    "How are delivery failures retried without creating duplicate records?",
    "What ordering, pagination, empty, loading, and error behavior should the UI use?",
    "Which boundary, retry, concurrency, and no-op cases require tests?",
)

ANSWER = {
    "due_soon": "Create once per loan at or after due_at - 24 hours, before due_at.",
    "due_now": "Create once per loan at or after due_at; returned loans are ignored.",
    "due_idempotency": "Uniqueness key is (patron_id, loan_id, notification_type).",
    "hold_order": "Order active holds by (created_at, id) ascending.",
    "hold_capacity": "For N copies, notify at most the first N unnotified holds.",
    "hold_idempotency": "Create at most one availability notification per hold.",
    "in_app": "Store notifications with created_at and unread/read state, newest first.",
    "production": "Use UTC, database uniqueness constraints, and transactional locking.",
    "delivery": "Commit an outbox event atomically and retry external delivery separately.",
    "testing": "Cover exact thresholds, retries, returned loans, FIFO ties, and zero copies.",
}


def acceptance_criteria() -> list[str]:
    return [f"{area}: {decision}" for area, decision in ANSWER.items()]


class Round4Tests(unittest.TestCase):
    def test_answer_covers_reported_constraints(self) -> None:
        summary = " ".join(acceptance_criteria()).lower()
        for requirement in ("24 hours", "idempotency", "first n", "created_at"):
            self.assertIn(requirement, summary)


if __name__ == "__main__":
    unittest.main()
