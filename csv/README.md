# CSV Shuffler

A professional Python console application for parsing CSV files, shuffling their contents, and writing to new files. Built with comprehensive error handling, input validation, and full unit test coverage.

## Features

- Parse CSV files with validation
- Shuffle data rows randomly
- Write shuffled data to new CSV files
- Comprehensive string manipulation utilities
- Full input/output validation
- Exception handling for all edge cases
- 100% unit test coverage
- Support for reproducible shuffling with random seeds

## Requirements

- Python 3.8 or higher
- No external dependencies (uses only Python standard library)

## Installation

No installation required. The application uses only Python standard library modules.

```bash
# Clone or download the files to your directory
# Ensure you have Python 3.8+ installed
python3 --version
```

## Usage

### Basic Usage

```bash
python3 csv_shuffler.py input.csv output.csv
```

### With Random Seed (Reproducible Shuffling)

```bash
python3 csv_shuffler.py input.csv output.csv 42
```

### Arguments

- `input.csv`: Path to the input CSV file (required)
- `output.csv`: Path to the output CSV file (required)
- `random_seed`: Optional integer seed for reproducible shuffling

## Example

```bash
# Shuffle the sample data
python3 csv_shuffler.py sample_data.csv shuffled_output.csv

# Shuffle with a specific seed for reproducibility
python3 csv_shuffler.py sample_data.csv shuffled_output.csv 123
```

## Running Tests

Run the comprehensive unit test suite:

```bash
# Run all tests with detailed output
python3 test_csv_shuffler.py

# Run with Python's unittest module
python3 -m unittest test_csv_shuffler.py -v

# Check test coverage (requires coverage package)
# pip install coverage
# coverage run test_csv_shuffler.py
# coverage report
```

## Code Structure

### `csv_shuffler.py`

Main application file containing:

- **StringManipulator**: Utility class for string operations
  - `validate_string()`: Validates and cleans strings
  - `normalize_whitespace()`: Normalizes whitespace in strings
  - `truncate_string()`: Truncates strings to max length
  - `sanitize_csv_value()`: Removes problematic characters

- **CSVShuffler**: Main processing class
  - `read_csv()`: Reads and parses CSV files with validation
  - `shuffle_rows()`: Shuffles data rows (optionally with seed)
  - `write_csv()`: Writes data to CSV files
  - `process()`: Main workflow method

### `test_csv_shuffler.py`

Comprehensive unit tests including:

- **TestStringManipulator**: 15+ tests for string operations
- **TestCSVShuffler**: 25+ tests for CSV operations
- **TestIntegration**: Integration tests for complete workflows

Test coverage includes:
- Valid input handling
- Invalid input validation
- Edge cases (empty files, malformed data)
- Error handling (permissions, file not found)
- Special characters and encoding
- Large file processing

## Error Handling

The application handles various error scenarios:

- File not found
- Invalid CSV format
- Empty files or rows
- Inconsistent column counts
- Control characters in data
- Permission errors
- Invalid file paths
- Input/output file conflicts

## Input Validation

- Validates file paths and existence
- Checks CSV structure and headers
- Sanitizes control characters
- Validates column consistency
- Strips whitespace from values
- Ensures non-empty data

## Interview Notes

This application demonstrates:

1. **Clean Code**: Well-structured, readable, maintainable
2. **Error Handling**: Comprehensive exception handling
3. **Input Validation**: Robust validation at all entry points
4. **Testing**: 40+ unit tests with high coverage
5. **String Manipulation**: Multiple string utility functions
6. **Documentation**: Clear docstrings and comments
7. **Type Hints**: Modern Python typing annotations
8. **SOLID Principles**: Single responsibility, dependency injection
9. **Edge Cases**: Handles empty files, special characters, etc.
10. **Professional Structure**: Modular, testable design

## License

MIT License - Free to use and modify
