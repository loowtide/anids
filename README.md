# anids

Network intrusion detection that actually runs on your machine. Capture live traffic or point it at a pcap file, and it'll tell you what's benign and what's not — using flow-level features and an XGBoost classifier.

## What it does

1. Captures packets via `tcpdump` (live mode) or reads an existing pcap
2. Extracts network flows using [cicflowmeter](https://github.com/hieulw/cicflowmeter) (Python port of CICFlowMeter)
3. Classifies each flow with a trained XGBoost model
4. Shows results in a live terminal table and logs them to CSV

## Requirements

- Python 3.13+
- `tcpdump` installed and accessible via `sudo`

## Setup

```bash
git clone <repo-url>
cd anids

# Install cicflowmeter from GitHub
uv add git+https://github.com/hieulw/cicflowmeter

# Install project dependencies
uv sync
```

> **Note:** `tcpdump` is invoked with `sudo` internally by the capture module, so you don't need to run anids live with sudo explicitly.

## Quick start

**Analyze a pcap file:**

```bash
anids file -f <file_path>.pcap
```

**Capture live traffic** (requires root for `tcpdump`):

```bash
sudo anids live -i wlan0
```

Press `Ctrl+C` to stop capturing. Results are logged to `anids/capture_data/results.csv` by default.

## Options

### `anids live`

| Flag                | What it does                       | Default                          |
| ------------------- | ---------------------------------- | -------------------------------- |
| `-i`, `--interface` | Network interface to sniff         | _required_                       |
| `-m`, `--model`     | XGBoost model file                 | `ml/models/xgb_model.pkl`        |
| `--rotate-secs`     | Seconds between pcap file rotation | `60`                             |
| `--outdir`          | Where to store pcap files          | `anids/capture_data/pcap`        |
| `--results-csv`     | Where to log results               | `anids/capture_data/results.csv` |

### `anids file`

| Flag             | What it does         | Default                             |
| ---------------- | -------------------- | ----------------------------------- |
| `-f`, `--file`   | Pcap file to analyze | _required_                          |
| `-m`, `--model`  | XGBoost model file   | `ml/models/xgb_model.pkl`           |
| `-o`, `--output` | Output CSV path      | `anids/capture_data/csv/<name>.csv` |
| `--results-csv`  | Where to log results | `anids/capture_data/results.csv`    |

## Training your own model

If you want to retrain the classifier instead of using the included model:

1. Place your training data in `ml/data/processed/train.csv`
2. Run `python ml/utils/train.py`

This saves the model, label encoder, and feature list to `ml/models/`.

## Project layout

```
anids/
├── anids/              # App code
│   ├── cli.py          # CLI entry point
│   ├── capture.py      # tcpdump wrapper
│   ├── flows.py        # pcap → flow CSV
│   ├── classifier.py   # Model loading & prediction
│   ├── pipeline.py     # Classification loop
│   ├── display.py      # Terminal UI
│   ├── csv_tail.py     # Tail results CSV
│   └── results_writer.py
├── ml/
│   ├── data/           # Raw and processed datasets
│   ├── models/         # Trained model + encoder
│   ├── notebooks/      # Jupyter notebooks
│   ├── scripts/        # Data processing scripts
│   └── utils/          # Training pipeline
│       ├── train.py    # Model training script
│       └── config.py   # Training configuration
└── pyproject.toml
```
