import signal
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from anids.capture import start_capture
from anids.classifier import FlowClassifier, ModelLoadError
from anids.csv_tail import CsvTail
from anids.display import build_table
from anids.flows import pcap_to_csv
from anids.pipeline import classify_new_rows
from anids.results_writer import ResultsWriter

app = typer.Typer(
    add_completion=False,
    help="anids: flow-based traffic classifier CLI",
)
console = Console()

DEFAULT_MODEL_DIR = Path("ml/models")
DEFAULT_MODEL = DEFAULT_MODEL_DIR / "xgb_model.pkl"
DEFAULT_ENCODER = DEFAULT_MODEL_DIR / "label_encoder.pkl"
DEFAULT_FEATURES = DEFAULT_MODEL_DIR / "expected_features.json"

DEFAULT_PCAP_DIR = Path("anids/capture_data/pcap")
DEFAULT_CSV_DIR = Path("anids/capture_data/csv")
DEFAULT_RESULTS_CSV = Path("anids/capture_data/results.csv")


def _load_classifier(
    model: Path,
    encoder: Path,
    features: Path,
) -> FlowClassifier:
    try:
        return FlowClassifier(
            model_path=model,
            encoder_path=encoder,
            features_path=features,
        )
    except ModelLoadError as e:
        console.print(f"[bold red]Failed to load model:[/bold red] {e}")
        raise typer.Exit(code=1)
    except FileNotFoundError as e:
        console.print(f"[bold red]Missing required file:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def live(
    interface: str = typer.Option(..., "-i", "--interface"),
    model: Path = typer.Option(DEFAULT_MODEL, "-m", "--model"),
    encoder: Path = typer.Option(DEFAULT_ENCODER, "--encoder"),
    features: Path = typer.Option(DEFAULT_FEATURES, "--features"),
    outdir: Path = typer.Option(DEFAULT_PCAP_DIR, "--outdir"),
    csvdir: Path = typer.Option(DEFAULT_CSV_DIR, "--csvdir"),
    results_csv: Path = typer.Option(
        DEFAULT_RESULTS_CSV,
        "--results-csv",
    ),
    rotate_secs: int = typer.Option(60, "--rotate-secs"),
    benign: str = typer.Option(
        "BENIGN,benign,Normal,normal",
        "--benign-labels",
    ),
):
    classifier = _load_classifier(model, encoder, features)
    benign_label = "benign"

    csvdir.mkdir(parents=True, exist_ok=True)
    results_writer = ResultsWriter(results_csv)

    console.print(
        Panel(
            f"Capturing on [bold]{interface}[/bold], "
            f"rotating every {rotate_secs}s — Ctrl+C to stop\n"
            f"Results log: [bold]{results_csv}[/bold]",
            style="bold cyan",
        )
    )

    session_start = time.time()
    proc = start_capture(
        interface=interface,
        outdir=str(outdir),
        rotate_secs=rotate_secs,
    )

    session_id = time.strftime("%Y%m%d_%H%M%S")
    session_csv = csvdir / f"capture_{session_id}.csv"
    rows: list[dict] = []
    stats = {"total": 0, "alerts": 0}
    processed_pcaps: set[str] = set()
    tail: CsvTail | None = None
    stopping = {"flag": False}

    def _handle_sigint(signum, frame):
        stopping["flag"] = True

    signal.signal(signal.SIGINT, _handle_sigint)

    def _process_finished_pcaps(include_newest: bool = False):
        nonlocal tail

        pcaps = sorted(
            p for p in outdir.glob("*.pcap") if p.stat().st_mtime >= session_start
        )

        if not pcaps:
            return

        candidates = pcaps if include_newest else pcaps[:-1]

        for pcap in candidates:
            if pcap.name in processed_pcaps:
                continue

            ok = pcap_to_csv(
                pcap,
                session_csv,
                append=True,
            )

            processed_pcaps.add(pcap.name)

            if not ok:
                continue

            if tail is None:
                tail = CsvTail(session_csv)

            classify_new_rows(
                tail.new_rows(),
                classifier=classifier,
                benign_label=benign_label,
                rows=rows,
                stats=stats,
                results_writer=results_writer,
            )

    try:
        with Live(console=console, refresh_per_second=4) as live_ui:
            while not stopping["flag"]:
                _process_finished_pcaps(include_newest=False)
                time.sleep(1.0)

            console.print("\n[dim]Stopping capture...[/dim]")

            proc.terminate()

            try:
                proc.wait(timeout=5)
            except Exception:
                proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
            time.sleep(1.0)

            _process_finished_pcaps(include_newest=True)

            live_ui.update(build_table(rows, stats))

    finally:
        if proc.poll() is None:
            proc.kill()

        results_writer.close()

    console.print(
        f"\n[bold]Done.[/bold] Total flows: {stats['total']}, "
        f"alerts: [bold red]{stats['alerts']}[/bold red]"
    )


@app.command(name="file")
def from_file(
    pcap: Path = typer.Option(..., "-f", "--file"),
    model: Path = typer.Option(DEFAULT_MODEL, "-m", "--model"),
    encoder: Path = typer.Option(DEFAULT_ENCODER, "--encoder"),
    features: Path = typer.Option(DEFAULT_FEATURES, "--features"),
    csv_out: Path = typer.Option(None, "-o", "--output"),
    results_csv: Path = typer.Option(
        DEFAULT_RESULTS_CSV,
        "--results-csv",
    ),
    benign: str = typer.Option(
        "BENIGN,benign,Normal,normal",
        "--benign-labels",
    ),
):
    if not pcap.exists():
        console.print(f"[bold red]File not found:[/bold red] {pcap}")
        raise typer.Exit(code=1)

    classifier = _load_classifier(model, encoder, features)
    benign_label = "benign"

    csv_out = csv_out or (DEFAULT_CSV_DIR / f"{pcap.stem}.csv")
    csv_out.parent.mkdir(parents=True, exist_ok=True)

    results_writer = ResultsWriter(results_csv)

    console.print(
        Panel(
            f"Processing [bold]{pcap.name}[/bold]",
            style="bold cyan",
        )
    )

    ok = pcap_to_csv(pcap, csv_out)

    if not ok:
        results_writer.close()
        console.print("[bold red]cicflowmeter failed, see error above.[/bold red]")
        raise typer.Exit(code=1)

    rows: list[dict] = []
    stats = {"total": 0, "alerts": 0}

    tail = CsvTail(csv_out)

    classify_new_rows(
        tail.new_rows(),
        classifier=classifier,
        benign_label=benign_label,
        rows=rows,
        stats=stats,
        results_writer=results_writer,
    )

    results_writer.close()

    console.print(build_table(rows, stats))

    console.print(
        f"\n[bold]Done.[/bold] Total flows: {stats['total']}, "
        f"alerts: [bold red]{stats['alerts']}[/bold red]"
    )


if __name__ == "__main__":
    app()
