from pathlib import Path

import polars as pl


class ROutputReader:
    def __init__(self, test_file_prefix):
        self.test_file_prefix = test_file_prefix

    def read(self, label):
        """Read R output from generated fixture file."""
        output_file = (
            Path("tests/fixtures/r_outputs") / f"{self.test_file_prefix}_{label}.rtf"
        )
        with open(output_file) as f:
            return f.read()


class TestData:
    """Data for testing."""

    @staticmethod
    def df1():
        data = {
            "Column1": ["Data 1.1", "Data 2.1"],
            "Column2": ["Data 1.2", "Data 2.2"],
        }
        return pl.DataFrame(data)
