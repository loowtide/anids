import csv
from pathlib import Path

RESULTS_FIELDS = ["src_ip", "dst_ip", "src_port", "dst_port", "class"]


class ResultsWriter:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        is_new = not self.path.exists() or self.path.stat().st_size == 0

        self._file = open(self.path, "a", newline="")
        self._writer = csv.DictWriter(self._file, fieldnames=RESULTS_FIELDS)
        if is_new:
            self._writer.writeheader()
            self._file.flush()

    def write(self, row: dict, label: str) -> None:
        self._writer.writerow(
            {
                "src_ip": row.get("src_ip", ""),
                "dst_ip": row.get("dst_ip", ""),
                "src_port": row.get("src_port", ""),
                "dst_port": row.get("dst_port", ""),
                "class": label,
            }
        )
        self._file.flush()

    def close(self):
        try:
            self._file.close()
        except Exception:
            pass

    def _enter(self):
        return self

    def __exit__(self, exc_type, exc_cal, exc_tb):
        self.close()
