"""Instacart / CodeSignal, Round 1: book-table requirement discovery.

RECONSTRUCTED QUESTION
Users say the library application's book table is too long and difficult to use.
Talk with the product manager to determine the requirements. The reported result
was a text search and two dropdown filters.

The exact PM responses were not published. The answer below is a concise model
conversation and requirement summary suitable for practice.
"""

import unittest


COMPANY = "Instacart"
PLATFORM = "CodeSignal"

CLARIFYING_QUESTIONS = (
    "Which book fields should the text input search?",
    "Should search be case-sensitive, exact, prefix, or substring matching?",
    "What dimensions should the two dropdowns filter by?",
    "How should search and dropdown filters combine?",
    "Should controls filter locally or request filtered results from the server?",
    "Should results update immediately or only after submission?",
    "What are the loading, empty-result, and error states?",
    "Must filters be represented in the URL and survive refresh/navigation?",
    "What accessibility and keyboard behavior is required?",
    "What unit and integration test coverage is expected?",
)

ANSWER = {
    "search": "Case-insensitive substring match against title and author.",
    "dropdown_1": "Genre, with an All genres option.",
    "dropdown_2": "Availability: All, Available, or Unavailable.",
    "combination": "All active controls use AND semantics.",
    "data_flow": "Send controls to the backend and do not filter again in the UI.",
    "updates": "Refresh whenever a control changes; suppress stale responses.",
    "states": "Show distinct initial/loading, success, empty, and error states.",
    "accessibility": "Use persistent labels, keyboard controls, and announced status.",
    "testing": "Cover each control, combined filters, states, and stale responses.",
}


def acceptance_criteria() -> list[str]:
    """Return an implementation-ready summary that can be given to a coding agent."""
    return [f"{area}: {decision}" for area, decision in ANSWER.items()]


class Round1Tests(unittest.TestCase):
    def test_answer_resolves_the_reported_feature(self) -> None:
        self.assertEqual(len(CLARIFYING_QUESTIONS), 10)
        self.assertIn("Genre", ANSWER["dropdown_1"])
        self.assertIn("Availability", ANSWER["dropdown_2"])
        self.assertIn("AND", ANSWER["combination"])


if __name__ == "__main__":
    unittest.main()
