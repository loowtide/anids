import time

from rich.console import Console

from anids.classifier import FlowClassifier
from anids.results_writer import ResultsWriter

console = Console()


def classify_new_rows(
    new_rows: list[dict],
    classifier: FlowClassifier,
    rows: list[dict],
    stats: dict,
    benign_label: str,
    results_writer: ResultsWriter | None = None,
) -> None:
    for row in new_rows:
        try:
            result = classifier.predict(row)
        except Exception as e:
            console.log(f"[yellow]Skipping row,prediction failed: {e}[/yellow]")
            continue

        is_attack = not (result["label"] == benign_label)
        stats["total"] += 1
        if is_attack:
            stats["alerts"] += 1

        if results_writer is not None:
            results_writer.write(row, result["label"])

        rows.append(
            {
                "time": time.strftime("%H:%M:%S"),
                "src_ip": row.get("src_ip", ""),
                "src_port": row.get("src_port", ""),
                "dst_ip": row.get("dst_ip", ""),
                "dst_port": row.get("dst_port", ""),
                "proto": str(row.get("proto", "")),
                "label": result["label"],
                "confidence": result["confidence"],
                "is_attack": is_attack,
            }
        )
