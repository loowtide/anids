import time
from pathlib import Path

from capture import start_capture
from flows import pcap_to_csv

PCAP_DIR = Path("capture/pcap")
CSV_DIR = Path("capture/csv")
INTERFACE = "wlan0"
CAPTURE_SECONDS = 20


def main():
    PCAP_DIR.mkdir(parents=True, exist_ok=True)
    CSV_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Startinig capture on {INTERFACE} for {CAPTURE_SECONDS}s...")
    proc = start_capture(
        interface=INTERFACE, outdir=str(PCAP_DIR), rotate_secs=CAPTURE_SECONDS
    )
    print(f"PID: {proc.pid}")

    time.sleep(CAPTURE_SECONDS + 2)
    proc.terminate()
    proc.wait()
    print("Capture stopped.")

    pcap_files = sorted(PCAP_DIR.glob("*.pcap"))
    if not pcap_files:
        print("No pcap files found.Check capture permissions")
        return

    latest_pcap = pcap_files[-1]
    csv_out = CSV_DIR / (latest_pcap.stem + ".csv")

    print(f"Converting {latest_pcap.stem}-> {csv_out.name}")
    success = pcap_to_csv(latest_pcap, csv_out)

    if success:
        print(f"Done. Flows written to {csv_out}")
    else:
        print("Conversion Failed. See error above.")


if __name__ == "__main__":
    main()
