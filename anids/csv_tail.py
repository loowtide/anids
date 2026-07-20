import csv
from pathlib import Path


class CsvTail:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._seen_rows = 0

    def new_rows(self) -> list[dict]:
        if not self.path.exists():
            return []
        with open(self.path, newline="") as f:
            reader = list(csv.DictReader(f))
        fresh = reader[self._seen_rows :]
        self._seen_rows = len(reader)
        return fresh
