import os
import subprocess
from pathlib import Path


def pcap_to_csv(pcap_path: str | Path, csv_out: str | Path, append: bool = False):
    pcap_path = str(pcap_path)
    csv_out = Path(csv_out)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    target = str(csv_out) + ".tmp" if append else str(csv_out)
    res = subprocess.run(
        ["cicflowmeter", "-f", pcap_path, "-c", target], capture_output=True, text=True
    )
    if res.returncode != 0:
        print(f"[ERROR] cicflowmeter failed on {pcap_path} ")
        print(res.stderr)
        if append and os.path.exists(target):
            os.remove(target)
        return False

    if not os.path.exists(target) or os.path.getsize(target) == 0:
        print(f"[OK] No flows extracted from {pcap_path}")
        if append and os.path.exists(target):
            os.remove(target)
        return True
    if append:
        write_header = not csv_out.exists() or csv_out.stat().st_size == 0
        with (
            open(target, "r", newline="") as src,
            open(csv_out, "a", newline="") as dst,
        ):
            lines = src.readlines()
            dst.writelines(lines if write_header else lines[1:])
        os.remove(target)
    print(f"[OK] Wrote flows to {csv_out}")
    return True
