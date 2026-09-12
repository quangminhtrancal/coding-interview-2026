"""Instacart / CodeSignal, Round 2: implement library search and filters.

RECONSTRUCTED QUESTION
Use an AI coding agent to add the text input and two dropdowns discovered in
Round 1, with full unit and integration coverage.

The report says the actual task was full-stack and included frontend JavaScript.
Because this collection was requested in Python, this answer implements and
tests the core server-side filtering contract in Python.
"""

from dataclasses import dataclass
from typing import Literal
import unittest


COMPANY = "Instacart"
PLATFORM = "CodeSignal"
Availability = Literal["all", "available", "unavailable"]


@dataclass(frozen=True)
class Book:
    id: int
    title: str
    author: str
    genre: str
    available_copies: int


def filter_books(
    books: list[Book],
    search: str = "",
    genre: str | None = None,
    availability: Availability = "all",
) -> list[Book]:
    """Apply case-insensitive search and AND-combined dropdown filters."""
    if availability not in {"all", "available", "unavailable"}:
        raise ValueError("availability must be all, available, or unavailable")

    needle = search.strip().casefold()
    result = []
    for book in books:
        matches_search = not needle or (
            needle in book.title.casefold() or needle in book.author.casefold()
        )
        matches_genre = not genre or book.genre.casefold() == genre.casefold()
        matches_availability = (
            availability == "all"
            or (availability == "available" and book.available_copies > 0)
            or (availability == "unavailable" and book.available_copies == 0)
        )
        if matches_search and matches_genre and matches_availability:
            result.append(book)
    return result


class Round2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.books = [
            Book(1, "Clean Code", "Robert Martin", "Technology", 2),
            Book(2, "Clean Architecture", "Robert Martin", "Technology", 0),
            Book(3, "The Hobbit", "J.R.R. Tolkien", "Fantasy", 1),
        ]

    def test_search_is_case_insensitive_and_checks_title_or_author(self) -> None:
        self.assertEqual([b.id for b in filter_books(self.books, "MARTIN")], [1, 2])

    def test_filters_use_and_semantics(self) -> None:
        result = filter_books(self.books, "clean", "technology", "available")
        self.assertEqual([book.id for book in result], [1])

    def test_empty_results_and_invalid_values(self) -> None:
        self.assertEqual(filter_books(self.books, "missing"), [])
        with self.assertRaises(ValueError):
            filter_books(self.books, availability="sometimes")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
