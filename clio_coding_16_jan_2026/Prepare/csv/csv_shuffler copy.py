import csv
import tempfile
import os
import pytest

def create_temp_csv(content):
    fd, path = tempfile.mkstemp(suffix='.csv')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(content)
    return path

def read_csv(path):
    try:
        with open(path, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                raise ValueError("CSV file is empty")

            rows = []
            for row in reader:
                if any(cell.strip() for cell in row):
                    rows.append(row)
        return headers, rows
    except Exception as e:
        raise ValueError(f'Having exception reading csv file {e}')

def write_csv(path, headers, rows):
    """Writes headers and rows to a CSV file."""
    try:
        with open(path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
    except Exception as e:
        raise ValueError(f'Having exception writing csv file {e}')

if __name__ == '__main__':
    # --- Test Read Logic ---
    # Note: Corrected the content to match your expected assertions ("Name" instead of "Thu")
    content = "Name,Age,City\nAlice,30,HCMC\nLoki,1,Calgary"
    path = create_temp_csv(content=content)

    try:
        headers, rows = read_csv(path)
        print(f'Testing Read: headers = {headers}')
        assert headers == ["Name", "Age", "City"]
        assert rows == [["Alice", "30", "HCMC"], ["Loki", "1", "Calgary"]]
        
        # --- Test Write Logic ---
        output_path = "test_output.csv"
        write_csv(output_path, headers, rows)
        
        # Verify the written file
        v_headers, v_rows = read_csv(output_path)
        assert v_headers == headers
        assert v_rows == rows
        
        print(f'Testing Write: Success')
        os.remove(output_path)
        print(f'Finish all tests')
        
    finally:
        if os.path.exists(path):
            os.remove(path)

    # --- Test Error Case ---
    content = "" # Empty file case
    path = create_temp_csv(content)
    try:
        with pytest.raises(ValueError, match="CSV file is empty"):
            read_csv(path)
    finally:
        if os.path.exists(path):
            os.remove(path)