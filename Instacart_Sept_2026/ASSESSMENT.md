# AI-Assisted Full-Stack Practice Assessment

## Scenario

You are working on Library Desk, an internal application used by librarians and
patrons. The existing catalog is difficult to navigate, one dashboard metric is
wrong, and patrons do not receive timely notifications.

Recommended time: 75 minutes. The five rounds intentionally combine requirement
discovery, code navigation, debugging, API design, React, and Python.

## Round 1: Requirements discovery (8 minutes)

A product manager says: "The book table is too long. Make it easier to find the
right books."

Write the questions you would ask before coding. Your final requirement summary
must resolve at least these topics:

- Searchable fields and whether matching is case-sensitive.
- The two useful dropdown filters.
- How multiple filters combine.
- Empty, loading, and failed-request states.
- Whether filtering is client-side or server-side.
- Accessibility expectations.

For this simulation, use the following final decisions:

- Search title and author with case-insensitive substring matching.
- Filter by `genre` and availability (`all`, `available`, `unavailable`).
- Combine active filters with AND semantics.
- Send filters to `GET /books`; do not reimplement filtering in the browser.
- Update results whenever a control changes.

Deliverable: a concise requirement summary and acceptance criteria.

## Round 2: React catalog integration (17 minutes)

Complete `frontend/BookCatalog.jsx` using this API:

```http
GET /books?search=clean&genre=Technology&availability=available
```

The response is a JSON array:

```json
[
  {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "genre": "Technology",
    "available_copies": 2,
    "total_copies": 3
  }
]
```

Acceptance criteria:

- Render labeled search, genre, and availability controls.
- Fetch on initial render and after a control changes.
- Ignore stale responses when controls change quickly.
- Render loading, error, empty, and success states.
- Preserve API snake_case fields at the boundary; conversion is optional.
- Do not filter the returned list again in React.

## Round 3: Debug the metrics endpoint (10 minutes)

The dashboard calls:

```http
GET /metrics/loans?from_date=2026-09-01&to_date=2026-09-30
```

It should report metrics for loans created inside the inclusive date range. The
production bug computes totals before applying the date filter, so the dashboard
shows all-time values.

Implement or review the endpoint so filtering happens before aggregation. Verify:

- Both date boundaries are inclusive.
- `returned` and `overdue` counts only use filtered loans.
- An invalid range (`from_date > to_date`) returns HTTP 422.
- No matching loans returns zeros.

The reference implementation and tests are in `backend/app.py` and
`backend/test_app.py`.

## Round 4: Notification requirement discovery (10 minutes)

A product manager says: "Notify patrons about due books and available holds."

Produce clarifying questions and acceptance criteria. For this simulation, the
resolved requirements are:

- Send one `due_soon` notification exactly 24 hours before a loan is due.
- Send one `due_now` notification when its due time is reached.
- A scheduler may retry; `(patron, loan, type)` must be idempotent.
- Patrons can hold the same book. Holds are served FIFO by creation time, then ID.
- When N copies become available, notify the first N waiting patrons.
- A hold availability notification is idempotent for a given hold.
- Notifications are in-app records with unread/read state.
- `GET /patrons/{id}/notifications` returns newest first.
- `PATCH /notifications/{id}/read` is idempotent.

Discuss how you would handle time zones, scheduler delays, simultaneous returns,
transactions, and failed delivery in a production system.

## Round 5: Full-stack notification implementation (30 minutes)

Backend API contract:

```http
POST  /jobs/due-notifications?now=2026-09-08T12:00:00Z
POST  /books/{book_id}/allocate-holds?available_copies=2
GET   /patrons/{patron_id}/notifications
PATCH /notifications/{notification_id}/read
```

Complete `frontend/NotificationCenter.jsx` and implement the backend behavior.

Acceptance criteria:

- Re-running either POST does not create duplicate notifications.
- Due processing handles both the 24-hour and due-now thresholds.
- Hold allocation respects deterministic FIFO order and available copy count.
- The notification center renders newest first and can mark an item read.
- Failed fetches are visible and retryable.
- Unit tests cover idempotency, boundaries, FIFO ordering, and no-op cases.

## Evaluation rubric

- Correct behavior and edge cases: 40%.
- Focused tests: 20%.
- API and component design: 15%.
- Requirement quality: 15%.
- Clear, efficient AI instructions and code navigation: 10%.
