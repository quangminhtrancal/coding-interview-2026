#!/usr/bin/env python3
"""
Unit tests for CSV Shuffler Application
"""

import unittest
import tempfile
import os
import csv
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from csv.csv_shuffler import StringManipulator, CSVShuffler


class TestStringManipulator(unittest.TestCase):
    """Test cases for StringManipulator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manipulator = StringManipulator()

    def test_validate_string_valid(self):
        """Test validation of valid strings."""
        result = self.manipulator.validate_string("  Hello World  ")
        self.assertEqual(result, "Hello World")

    def test_validate_string_empty(self):
        """Test validation rejects empty strings."""
        with self.assertRaises(ValueError) as context:
            self.manipulator.validate_string("")
        self.assertIn("cannot be empty", str(context.exception))

    def test_validate_string_whitespace_only(self):
        """Test validation rejects whitespace-only strings."""
        with self.assertRaises(ValueError) as context:
            self.manipulator.validate_string("   ")
        self.assertIn("cannot be empty", str(context.exception))

    def test_validate_string_not_string_type(self):
        """Test validation rejects non-string types."""
        with self.assertRaises(ValueError) as context:
            self.manipulator.validate_string(123)
        self.assertIn("must be a string", str(context.exception))

    def test_validate_string_custom_field_name(self):
        """Test validation uses custom field name in error messages."""
        with self.assertRaises(ValueError) as context:
            self.manipulator.validate_string("", "Username")
        self.assertIn("Username", str(context.exception))

    def test_normalize_whitespace_multiple_spaces(self):
        """Test normalization of multiple spaces."""
        result = self.manipulator.normalize_whitespace("Hello    World")
        self.assertEqual(result, "Hello World")

    def test_normalize_whitespace_tabs_newlines(self):
        """Test normalization of tabs and newlines."""
        result = self.manipulator.normalize_whitespace("Hello\t\n  World")
        self.assertEqual(result, "Hello World")

    def test_normalize_whitespace_already_normalized(self):
        """Test normalization of already normalized string."""
        result = self.manipulator.normalize_whitespace("Hello World")
        self.assertEqual(result, "Hello World")

    def test_truncate_string_no_truncation_needed(self):
        """Test truncation when string is shorter than max length."""
        result = self.manipulator.truncate_string("Hello", 10)
        self.assertEqual(result, "Hello")

    def test_truncate_string_exact_length(self):
        """Test truncation when string equals max length."""
        result = self.manipulator.truncate_string("Hello", 5)
        self.assertEqual(result, "Hello")

    def test_truncate_string_truncation_needed(self):
        """Test truncation when string exceeds max length."""
        result = self.manipulator.truncate_string("Hello World", 5)
        self.assertEqual(result, "Hello")

    def test_truncate_string_invalid_max_length(self):
        """Test truncation with invalid max length."""
        with self.assertRaises(ValueError) as context:
            self.manipulator.truncate_string("Hello", 0)
        self.assertIn("must be positive", str(context.exception))

        with self.assertRaises(ValueError):
            self.manipulator.truncate_string("Hello", -1)

    def test_sanitize_csv_value_clean_string(self):
        """Test sanitization of clean string."""
        result = self.manipulator.sanitize_csv_value("Hello World")
        self.assertEqual(result, "Hello World")

    def test_sanitize_csv_value_with_control_chars(self):
        """Test sanitization removes control characters."""
        result = self.manipulator.sanitize_csv_value("Hello\x00\x01World")
        self.assertEqual(result, "HelloWorld")

    def test_sanitize_csv_value_preserves_newlines(self):
        """Test sanitization preserves newlines."""
        result = self.manipulator.sanitize_csv_value("Hello\nWorld")
        self.assertEqual(result, "Hello\nWorld")

    def test_sanitize_csv_value_strips_whitespace(self):
        """Test sanitization strips leading/trailing whitespace."""
        result = self.manipulator.sanitize_csv_value("  Hello World  ")
        self.assertEqual(result, "Hello World")


class TestCSVShuffler(unittest.TestCase):
    """Test cases for CSVShuffler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.shuffler = CSVShuffler()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_temp_csv(self, filename, headers, rows):
        """Helper to create a temporary CSV file."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        return filepath

    def test_validate_file_path_valid_existing_file(self):
        """Test validation of valid existing file path."""
        filepath = self.create_temp_csv("test.csv", ["A"], [["1"]])
        result = self.shuffler.validate_file_path(filepath, check_exists=True)
        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), filepath)

    def test_validate_file_path_nonexistent_file(self):
        """Test validation raises error for nonexistent file."""
        filepath = os.path.join(self.temp_dir, "nonexistent.csv")
        with self.assertRaises(FileNotFoundError):
            self.shuffler.validate_file_path(filepath, check_exists=True)

    def test_validate_file_path_directory_not_file(self):
        """Test validation raises error when path is a directory."""
        with self.assertRaises(ValueError) as context:
            self.shuffler.validate_file_path(self.temp_dir, check_exists=True)
        self.assertIn("not a file", str(context.exception))

    def test_validate_file_path_skip_exists_check(self):
        """Test validation can skip existence check."""
        filepath = os.path.join(self.temp_dir, "nonexistent.csv")
        result = self.shuffler.validate_file_path(filepath, check_exists=False)
        self.assertIsInstance(result, Path)

    def test_read_csv_valid_file(self):
        """Test reading a valid CSV file."""
        filepath = self.create_temp_csv(
            "test.csv",
            ["Name", "Age", "City"],
            [["Alice", "30", "NYC"], ["Bob", "25", "LA"]]
        )

        headers, rows = self.shuffler.read_csv(filepath)

        self.assertEqual(headers, ["Name", "Age", "City"])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ["Alice", "30", "NYC"])
        self.assertEqual(rows[1], ["Bob", "25", "LA"])

    def test_read_csv_empty_file(self):
        """Test reading an empty CSV file raises error."""
        filepath = os.path.join(self.temp_dir, "empty.csv")
        with open(filepath, 'w') as f:
            pass

        with self.assertRaises(ValueError) as context:
            self.shuffler.read_csv(filepath)
        self.assertIn("empty", str(context.exception).lower())

    def test_read_csv_no_data_rows(self):
        """Test reading CSV with headers but no data raises error."""
        filepath = self.create_temp_csv("nodata.csv", ["A", "B"], [])

        with self.assertRaises(ValueError) as context:
            self.shuffler.read_csv(filepath)
        self.assertIn("no data rows", str(context.exception).lower())

    def test_read_csv_inconsistent_columns(self):
        """Test reading CSV with inconsistent column count raises error."""
        filepath = os.path.join(self.temp_dir, "bad.csv")
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["A", "B", "C"])
            writer.writerow(["1", "2", "3"])
            writer.writerow(["4", "5"])  # Wrong number of columns

        with self.assertRaises(ValueError) as context:
            self.shuffler.read_csv(filepath)
        self.assertIn("columns", str(context.exception).lower())

    def test_read_csv_skips_empty_rows(self):
        """Test reading CSV skips empty rows."""
        filepath = os.path.join(self.temp_dir, "empty_rows.csv")
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["A", "B"])
            writer.writerow(["1", "2"])
            writer.writerow(["", ""])  # Empty row
            writer.writerow(["3", "4"])

        headers, rows = self.shuffler.read_csv(filepath)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ["1", "2"])
        self.assertEqual(rows[1], ["3", "4"])

    def test_read_csv_sanitizes_values(self):
        """Test reading CSV sanitizes control characters."""
        filepath = os.path.join(self.temp_dir, "dirty.csv")
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Name"])
            writer.writerow(["Alice\x00Bob"])

        headers, rows = self.shuffler.read_csv(filepath)
        self.assertEqual(rows[0][0], "AliceBob")

    def test_read_csv_nonexistent_file(self):
        """Test reading nonexistent file raises error."""
        with self.assertRaises(FileNotFoundError):
            self.shuffler.read_csv(os.path.join(self.temp_dir, "none.csv"))

    def test_shuffle_rows_basic(self):
        """Test basic row shuffling."""
        rows = [["1"], ["2"], ["3"], ["4"], ["5"]]
        shuffled = self.shuffler.shuffle_rows(rows, seed=42)

        self.assertEqual(len(shuffled), len(rows))
        self.assertNotEqual(shuffled, rows)  # Should be different order
        self.assertEqual(set(tuple(r) for r in shuffled), set(tuple(r) for r in rows))

    def test_shuffle_rows_reproducible_with_seed(self):
        """Test shuffling is reproducible with same seed."""
        rows = [["1"], ["2"], ["3"], ["4"], ["5"]]

        shuffled1 = self.shuffler.shuffle_rows(rows, seed=42)
        shuffled2 = self.shuffler.shuffle_rows(rows, seed=42)

        self.assertEqual(shuffled1, shuffled2)

    def test_shuffle_rows_different_with_different_seed(self):
        """Test shuffling is different with different seeds."""
        rows = [["1"], ["2"], ["3"], ["4"], ["5"]]

        shuffled1 = self.shuffler.shuffle_rows(rows, seed=42)
        shuffled2 = self.shuffler.shuffle_rows(rows, seed=99)

        self.assertNotEqual(shuffled1, shuffled2)

    def test_shuffle_rows_does_not_modify_original(self):
        """Test shuffling doesn't modify the original list."""
        rows = [["1"], ["2"], ["3"]]
        original = [["1"], ["2"], ["3"]]

        self.shuffler.shuffle_rows(rows, seed=42)

        self.assertEqual(rows, original)

    def test_shuffle_rows_empty_list(self):
        """Test shuffling empty list raises error."""
        with self.assertRaises(ValueError) as context:
            self.shuffler.shuffle_rows([])
        self.assertIn("empty", str(context.exception).lower())

    def test_shuffle_rows_invalid_input(self):
        """Test shuffling with invalid input raises error."""
        with self.assertRaises(ValueError) as context:
            self.shuffler.shuffle_rows("not a list")
        self.assertIn("must be a list", str(context.exception))

    def test_write_csv_valid(self):
        """Test writing a valid CSV file."""
        output_file = os.path.join(self.temp_dir, "output.csv")
        headers = ["Name", "Age"]
        rows = [["Alice", "30"], ["Bob", "25"]]

        self.shuffler.write_csv(output_file, headers, rows)

        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            read_headers = next(reader)
            read_rows = list(reader)

        self.assertEqual(read_headers, headers)
        self.assertEqual(read_rows, rows)

    def test_write_csv_creates_parent_directory(self):
        """Test writing creates parent directories if needed."""
        output_file = os.path.join(self.temp_dir, "subdir", "output.csv")
        headers = ["A"]
        rows = [["1"]]

        self.shuffler.write_csv(output_file, headers, rows)

        self.assertTrue(os.path.exists(output_file))

    def test_write_csv_empty_headers(self):
        """Test writing with empty headers raises error."""
        output_file = os.path.join(self.temp_dir, "output.csv")

        with self.assertRaises(ValueError) as context:
            self.shuffler.write_csv(output_file, [], [["1"]])
        self.assertIn("empty", str(context.exception).lower())

    def test_write_csv_empty_rows(self):
        """Test writing with empty rows raises error."""
        output_file = os.path.join(self.temp_dir, "output.csv")

        with self.assertRaises(ValueError) as context:
            self.shuffler.write_csv(output_file, ["A"], [])
        self.assertIn("empty", str(context.exception).lower())

    def test_write_csv_permission_error(self):
        """Test writing to protected location raises PermissionError."""
        # Create a read-only directory
        readonly_dir = os.path.join(self.temp_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)

        output_file = os.path.join(readonly_dir, "output.csv")

        try:
            with self.assertRaises(PermissionError):
                self.shuffler.write_csv(output_file, ["A"], [["1"]])
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)

    def test_process_complete_workflow(self):
        """Test complete processing workflow."""
        input_file = self.create_temp_csv(
            "input.csv",
            ["Name", "Score"],
            [["Alice", "100"], ["Bob", "85"], ["Charlie", "90"]]
        )
        output_file = os.path.join(self.temp_dir, "output.csv")

        result = self.shuffler.process(input_file, output_file, seed=42)

        # Verify result dictionary
        self.assertEqual(result['rows_processed'], 3)
        self.assertEqual(result['columns'], 2)
        self.assertTrue(os.path.exists(output_file))

        # Verify output file content
        with open(output_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)

        self.assertEqual(headers, ["Name", "Score"])
        self.assertEqual(len(rows), 3)
        # Rows should be shuffled (different order)
        self.assertNotEqual(
            rows,
            [["Alice", "100"], ["Bob", "85"], ["Charlie", "90"]]
        )

    def test_process_same_input_output_file(self):
        """Test processing raises error when input and output are same."""
        input_file = self.create_temp_csv("test.csv", ["A"], [["1"]])

        with self.assertRaises(ValueError) as context:
            self.shuffler.process(input_file, input_file)
        self.assertIn("cannot be the same", str(context.exception).lower())

    def test_process_nonexistent_input(self):
        """Test processing nonexistent input file raises error."""
        input_file = os.path.join(self.temp_dir, "none.csv")
        output_file = os.path.join(self.temp_dir, "output.csv")

        with self.assertRaises(FileNotFoundError):
            self.shuffler.process(input_file, output_file)

    def test_dependency_injection_string_manipulator(self):
        """Test CSVShuffler accepts custom StringManipulator."""
        mock_manipulator = Mock(spec=StringManipulator)
        shuffler = CSVShuffler(string_manipulator=mock_manipulator)

        self.assertEqual(shuffler.string_manipulator, mock_manipulator)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.shuffler = CSVShuffler()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_large_csv_file(self):
        """Test processing a large CSV file."""
        # Create a CSV with 1000 rows
        input_file = os.path.join(self.temp_dir, "large.csv")
        output_file = os.path.join(self.temp_dir, "large_out.csv")

        with open(input_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Value"])
            for i in range(1000):
                writer.writerow([str(i), f"Name{i}", f"Value{i}"])

        result = self.shuffler.process(input_file, output_file, seed=123)

        self.assertEqual(result['rows_processed'], 1000)
        self.assertTrue(os.path.exists(output_file))

        # Verify all data is preserved
        with open(output_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip headers
            output_rows = list(reader)

        self.assertEqual(len(output_rows), 1000)

    def test_special_characters_in_data(self):
        """Test processing CSV with special characters."""
        input_file = os.path.join(self.temp_dir, "special.csv")
        output_file = os.path.join(self.temp_dir, "special_out.csv")

        with open(input_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Description"])
            writer.writerow(["O'Neill", "Quote: \"Hello\""])
            writer.writerow(["Smith", "Comma, semicolon;"])
            writer.writerow(["José", "Ñoño café"])

        result = self.shuffler.process(input_file, output_file, seed=42)

        self.assertEqual(result['rows_processed'], 3)

        # Verify special characters preserved
        with open(output_file, 'r', encoding='utf-8', newline='') as f:
            content = f.read()
            self.assertIn("O'Neill", content)
            self.assertIn("José", content)
            self.assertIn("Ñoño", content)


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStringManipulator))
    suite.addTests(loader.loadTestsFromTestCase(TestCSVShuffler))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == "__main__":
    result = run_tests()
    exit(0 if result.wasSuccessful() else 1)
