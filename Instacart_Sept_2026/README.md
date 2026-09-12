# Instacart-Style AI-Assisted Full-Stack Practice

This is an original practice assessment inspired by the public experience report in
`~/Downloads/Instacart Full-Stack Engineer Assessment on CodeSignal _ r_InterviewDB.pdf`.
It is not a copy of Instacart or CodeSignal assessment content.

The simulation uses a library application because that is the domain described in
the report. It covers five rounds:

1. Gather requirements for book search and filters.
2. Implement the search/filter user interface in React.
3. Find and fix a metrics calculation bug in Python.
4. Gather requirements for due-date and hold notifications.
5. Implement and integrate the notification feature.

## Layout

- `ASSESSMENT.md`: timed candidate instructions and all five questions.
- `frontend/BookCatalog.jsx`: React starter for Round 2.
- `frontend/NotificationCenter.jsx`: React starter for Round 5.
- `backend/app.py`: complete FastAPI reference solution.
- `backend/test_app.py`: executable scenarios corresponding to the assessment.
- `backend/requirements.txt`: Python dependencies.

## Run the backend tests

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Run the API

```bash
cd backend
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/docs` for the generated API documentation.

## Suggested practice format

Use a 75-minute timer. Read only `ASSESSMENT.md` and the two files in `frontend/`
at first. Keep `backend/app.py` as a reference solution and compare it with your
implementation after the timer expires.
