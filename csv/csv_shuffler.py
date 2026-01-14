#!/usr/bin/env python3
"""
CSV Shuffler Application
Parses a CSV file, shuffles its content, and writes to a new file.
"""

import csv
import random
import sys
import os
from typing import List, Optional
from pathlib import Path


class StringManipulator:
    """Utility class for string manipulation and validation."""

    @staticmethod
    def validate_string(value: str, field_name: str = "Field") -> str:
        """
        Validate and clean a string value.

        Args:
            value: The string to validate
            field_name: Name of the field for error messages

        Returns:
            Cleaned string value

        Raises:
            ValueError: If string is empty or invalid
        """
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")

        cleaned = value.strip()
        if not cleaned:
            raise ValueError(f"{field_name} cannot be empty or whitespace only")

        return cleaned

    @staticmethod
    def normalize_whitespace(value: str) -> str:
        """
        Normalize whitespace in a string (collapse multiple spaces to single space).

        Args:
            value: The string to normalize

        Returns:
            String with normalized whitespace
        """
        return ' '.join(value.split())

    @staticmethod
    def truncate_string(value: str, max_length: int) -> str:
        """
        Truncate a string to a maximum length.

        Args:
            value: The string to truncate
            max_length: Maximum allowed length

        Returns:
            Truncated string

        Raises:
            ValueError: If max_length is invalid
        """
        if max_length <= 0:
            raise ValueError("max_length must be positive")

        return value[:max_length] if len(value) > max_length else value

    @staticmethod
    def sanitize_csv_value(value: str) -> str:
        """
        Sanitize a CSV value by removing or escaping problematic characters.

        Args:
            value: The value to sanitize

        Returns:
            Sanitized string
        """
        # Remove null bytes and control characters except newlines
        sanitized = ''.join(char for char in value if char == '\n' or ord(char) >= 32)
        return sanitized.strip()


class CSVShuffler:
    """Handles CSV file parsing, shuffling, and writing operations."""

    def __init__(self, string_manipulator: Optional[StringManipulator] = None):
        """
        Initialize CSV Shuffler.

        Args:
            string_manipulator: Optional StringManipulator instance for dependency injection
        """
        self.string_manipulator = string_manipulator or StringManipulator()

    def validate_file_path(self, file_path: str, check_exists: bool = True) -> Path:
        """
        Validate a file path.

        Args:
            file_path: Path to validate
            check_exists: Whether to check if file exists

        Returns:
            Path object

        Raises:
            FileNotFoundError: If file doesn't exist and check_exists is True
            ValueError: If path is invalid
        """
        try:
            path = Path(file_path)
        except Exception as e:
            raise ValueError(f"Invalid file path: {e}")

        if check_exists and not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if check_exists and not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        return path

    def read_csv(self, input_file: str) -> tuple[List[str], List[List[str]]]:
        """
        Read and parse a CSV file.

        Args:
            input_file: Path to the input CSV file

        Returns:
            Tuple of (headers, rows)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty or invalid CSV format
            Exception: For other read errors
        """
        input_path = self.validate_file_path(input_file, check_exists=True)

        try:
            with open(input_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)

                # Read headers
                try:
                    headers = next(reader)
                except StopIteration:
                    raise ValueError("CSV file is empty")

                if not headers:
                    raise ValueError("CSV file has no headers")

                # Validate and clean headers
                cleaned_headers = []
                for i, header in enumerate(headers):
                    try:
                        cleaned = self.string_manipulator.validate_string(header, f"Header {i}")
                        cleaned = self.string_manipulator.sanitize_csv_value(cleaned)
                        cleaned_headers.append(cleaned)
                    except ValueError as e:
                        raise ValueError(f"Invalid header at position {i}: {e}")

                # Read data rows
                rows = []
                for row_num, row in enumerate(reader, start=2):
                    if not row or all(not cell.strip() for cell in row):
                        continue  # Skip empty rows

                    # Validate row has correct number of columns
                    if len(row) != len(cleaned_headers):
                        raise ValueError(
                            f"Row {row_num} has {len(row)} columns, expected {len(cleaned_headers)}"
                        )

                    # Clean each cell
                    cleaned_row = [
                        self.string_manipulator.sanitize_csv_value(cell)
                        for cell in row
                    ]
                    rows.append(cleaned_row)

                if not rows:
                    raise ValueError("CSV file has no data rows")

                return cleaned_headers, rows

        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")

    def shuffle_rows(self, rows: List[List[str]], seed: Optional[int] = None) -> List[List[str]]:
        """
        Shuffle the rows of data.

        Args:
            rows: List of rows to shuffle
            seed: Optional random seed for reproducible shuffling

        Returns:
            Shuffled list of rows

        Raises:
            ValueError: If rows is empty or invalid
        """
        if not rows:
            raise ValueError("Cannot shuffle empty rows")

        if not isinstance(rows, list):
            raise ValueError("Rows must be a list")

        # Create a copy to avoid modifying original
        shuffled = rows.copy()

        if seed is not None:
            random.seed(seed)

        random.shuffle(shuffled)
        return shuffled

    def write_csv(self, output_file: str, headers: List[str], rows: List[List[str]]) -> None:
        """
        Write data to a CSV file.

        Args:
            output_file: Path to the output CSV file
            headers: List of column headers
            rows: List of data rows

        Raises:
            ValueError: If headers or rows are invalid
            PermissionError: If cannot write to file
            Exception: For other write errors
        """
        if not headers:
            raise ValueError("Headers cannot be empty")

        if not rows:
            raise ValueError("Rows cannot be empty")

        output_path = Path(output_file)

        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
        except PermissionError:
            raise PermissionError(f"Permission denied writing to: {output_file}")
        except Exception as e:
            raise Exception(f"Error writing CSV file: {e}")

    def process(self, input_file: str, output_file: str, seed: Optional[int] = None) -> dict:
        """
        Main processing method: read, shuffle, and write CSV.

        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file
            seed: Optional random seed

        Returns:
            Dictionary with processing statistics

        Raises:
            Various exceptions from read/write operations
        """
        # Validate output path doesn't overwrite input
        input_path = self.validate_file_path(input_file, check_exists=True)
        output_path = Path(output_file)

        if input_path.resolve() == output_path.resolve():
            raise ValueError("Output file cannot be the same as input file")

        # Read CSV
        headers, rows = self.read_csv(input_file)
        original_count = len(rows)

        # Shuffle
        shuffled_rows = self.shuffle_rows(rows, seed=seed)

        # Write
        self.write_csv(output_file, headers, shuffled_rows)

        return {
            'input_file': str(input_path),
            'output_file': str(output_path.resolve()),
            'rows_processed': original_count,
            'columns': len(headers)
        }


def main():
    """Main entry point for the console application."""
    if len(sys.argv) < 3:
        print("Usage: python csv_shuffler.py <input_file.csv> <output_file.csv> [random_seed]")
        print("\nArguments:")
        print("  input_file.csv   Path to the input CSV file")
        print("  output_file.csv  Path to the output CSV file")
        print("  random_seed      Optional integer seed for reproducible shuffling")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    seed = None

    if len(sys.argv) >= 4:
        try:
            seed = int(sys.argv[3])
        except ValueError:
            print(f"Error: Invalid random seed '{sys.argv[3]}'. Must be an integer.")
            sys.exit(1)

    shuffler = CSVShuffler()

    try:
        print(f"Reading CSV from: {input_file}")
        result = shuffler.process(input_file, output_file, seed=seed)

        print("\n✓ Success!")
        print(f"  Processed: {result['rows_processed']} rows")
        print(f"  Columns: {result['columns']}")
        print(f"  Output written to: {result['output_file']}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
