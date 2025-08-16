import pytest
from src.csv_processor import CSVProcessor
import os
import pandas as pd

def test_load_csv_file_not_found():
    processor = CSVProcessor("not_exist.csv")
    with pytest.raises(FileNotFoundError):
        processor.load_csv()

def test_handle_missing_values_fill(tmp_path):
    # テスト用CSV作成
    csv_path = tmp_path / "test.csv"
    df = pd.DataFrame({"A": [1, None, 3], "B": ["x", None, "z"]})
    df.to_csv(csv_path, index=False)
    processor = CSVProcessor(str(csv_path))
    processor.load_csv()
    processed = processor.handle_missing_values(strategy="fill")
    assert processed.isnull().sum().sum() == 0
