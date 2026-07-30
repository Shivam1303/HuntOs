"""Contract tests for the distributable opportunity sample CSV."""

import csv
from io import StringIO
from pathlib import Path

from modules.opportunities.csv_columns import SUPPORTED_CSV_COLUMNS
from modules.opportunities.csv_importer import import_csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV = PROJECT_ROOT / "sample_opportunities.csv"


def test_sample_csv_uses_canonical_headers_and_valid_rows() -> None:
    """Keep the sample executable as documentation for every supported field."""

    content = SAMPLE_CSV.read_bytes()
    text = content.decode("utf-8-sig")
    headers = next(csv.reader(StringIO(text, newline="")))

    assert tuple(headers) == SUPPORTED_CSV_COLUMNS

    result = import_csv(content)

    assert result.total_rows >= 2
    assert result.valid_count == result.total_rows
    assert result.rejected_count == 0
    assert result.opportunities[0].source_id is not None
    assert result.opportunities[0].posted_at is not None
