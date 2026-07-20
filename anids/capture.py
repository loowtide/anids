import os
import subprocess


def start_capture(
    interface="wlan0", outdir="capture_data/pcap", rotate_secs=60, snaplen=0
):
    os.makedirs(outdir, exist_ok=True)
    cmd = [
        "sudo",
        "tcpdump",
        "-i",
        interface,
        "-s",
        str(snaplen),
        "-w",
        f"{outdir}/capture_%Y%m%d_%H%M%S.pcap",
        "-G",
        str(rotate_secs),
        "-Z",
        "root",
        "-nn",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return proc
