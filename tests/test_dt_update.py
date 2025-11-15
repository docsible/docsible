import os
import pytest
import yaml
from datetime import datetime
from unittest.mock import patch
from docsible.cli import manage_docsible_file_keys

def test_dt_update():
    test_file = ".docsible_test_dt_update"

    try:
        # Mock datetime to return a fixed date
        fixed_date = datetime(2025, 11, 12, 10, 30, 0)
        expected_date_str = '2025/11/12'

        with patch('docsible.cli.datetime') as mock_datetime:
            mock_datetime.now.return_value = fixed_date
            mock_datetime.strftime = datetime.strftime

            manage_docsible_file_keys(test_file)

        with open(test_file, "r") as f:
            data = yaml.safe_load(f)

        assert data['dt_update'] == expected_date_str

    finally:
        # Cleanup: remove the test file if it exists
        if os.path.exists(test_file):
            os.remove(test_file)
