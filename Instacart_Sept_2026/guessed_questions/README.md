# Instacart CodeSignal Guessed Questions and Python Answers

**Company:** Instacart  
**Platform:** CodeSignal  
**Assessment:** Instacart Full-Stack Engineer Assessment

These are reconstructed practice questions, not leaked or verbatim assessment
content. They are based on the public experience report saved as:

`~/Downloads/Instacart Full-Stack Engineer Assessment on CodeSignal _ r_InterviewDB.pdf`

The report confirms the five-round structure and broad behaviors, but does not
provide the original prompts, starter repository, API contract, field names, or
exact UI labels. Details not present in the report are clearly treated as
reasonable practice assumptions.

## Reported Questions

1. `instacart_round_1_requirements.py`: clarify requirements for shortening a
   difficult-to-use library book table using a text search and two dropdowns.
2. `instacart_round_2_book_filters.py`: implement the search/filter feature and
   cover it with tests. The real round reportedly involved a frontend; this file
   gives a Python implementation of the same business behavior.
3. `instacart_round_3_metrics_debugging.py`: fix a Python backend metrics bug in
   which aggregation occurs before filtering.
4. `instacart_round_4_notification_requirements.py`: clarify requirements for
   due-date and hold-availability notifications, including idempotency and FIFO.
5. `instacart_round_5_notifications.py`: implement the notification behavior,
   including tests for timing, idempotency, and FIFO allocation.

## Run All Answers

Only the Python standard library is required.

```bash
python3 -m unittest discover -s . -p 'instacart_round_*.py' -v
```

## Confidence

- High: five rounds; library domain; search plus two dropdowns; Python filtering
  bug; due notifications at 24 hours and due time; FIFO hold notifications for
  the first N patrons; idempotency; expected tests.
- Inferred: precise data models, function signatures, dropdown meanings, exact
  date metric, endpoint shapes, and edge-case decisions.
