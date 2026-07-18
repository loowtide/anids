import subprocess
from pathlib import Path


def pcap_to_csv(pcap_path: str | Path, csv_out: str | Path):
    pcap_path = str(pcap_path)
    csv_out = str(csv_out)
    Path(csv_out).parent.mkdir(parents=True, exist_ok=True)
    res = subprocess.run(
        ["cicflowmeter", "-f", pcap_path, "-c", csv_out], capture_output=True, text=True
    )
    if res.returncode != 0:
        print(f"[ERROR] cicflowmeter failed on {pcap_path} ")
        print(res.stderr)
        return False
    print(f"[OK] Wrote flows to {csv_out}")
    return True
