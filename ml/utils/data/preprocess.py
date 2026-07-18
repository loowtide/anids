from pathlib import Path

import pandas as pd

# removing Src IP,Dst IP,Timestamp,Source File from datasets
input_dir = Path("../../data/raw")
output_dir = Path("../../data/clean")
output_dir.mkdir(parents=True, exist_ok=True)

cols_to_drop = ["src_ip", "dst_ip", "timestamp", "Source File"]
COLUMN_MAP = {
    "Src IP": "src_ip",
    "Src Port": "src_port",
    "Dst IP": "dst_ip",
    "Dst Port": "dst_port",
    "Protocol": "protocol",
    "Timestamp": "timestamp",
    "Flow Duration": "flow_duration",
    "Tot Fwd Pkts": "tot_fwd_pkts",
    "Tot Bwd Pkts": "tot_bwd_pkts",
    "TotLen Fwd Pkts": "totlen_fwd_pkts",
    "TotLen Bwd Pkts": "totlen_bwd_pkts",
    "Fwd Pkt Len Max": "fwd_pkt_len_max",
    "Fwd Pkt Len Min": "fwd_pkt_len_min",
    "Fwd Pkt Len Mean": "fwd_pkt_len_mean",
    "Fwd Pkt Len Std": "fwd_pkt_len_std",
    "Bwd Pkt Len Max": "bwd_pkt_len_max",
    "Bwd Pkt Len Min": "bwd_pkt_len_min",
    "Bwd Pkt Len Mean": "bwd_pkt_len_mean",
    "Bwd Pkt Len Std": "bwd_pkt_len_std",
    "Pkt Len Min": "pkt_len_min",
    "Pkt Len Max": "pkt_len_max",
    "Pkt Len Mean": "pkt_len_mean",
    "Pkt Len Std": "pkt_len_std",
    "Pkt Len Var": "pkt_len_var",
    "Flow Pkts/s": "flow_pkts_s",
    "Flow Byts/s": "flow_byts_s",
    "Flow IAT Mean": "flow_iat_mean",
    "Flow IAT Std": "flow_iat_std",
    "Flow IAT Max": "flow_iat_max",
    "Flow IAT Min": "flow_iat_min",
    "Fwd IAT Tot": "fwd_iat_tot",
    "Fwd IAT Mean": "fwd_iat_mean",
    "Fwd IAT Std": "fwd_iat_std",
    "Fwd IAT Max": "fwd_iat_max",
    "Fwd IAT Min": "fwd_iat_min",
    "Bwd IAT Tot": "bwd_iat_tot",
    "Bwd IAT Mean": "bwd_iat_mean",
    "Bwd IAT Std": "bwd_iat_std",
    "Bwd IAT Max": "bwd_iat_max",
    "Bwd IAT Min": "bwd_iat_min",
    "Fwd PSH Flags": "fwd_psh_flags",
    "Bwd PSH Flags": "bwd_psh_flags",
    "Fwd URG Flags": "fwd_urg_flags",
    "Bwd URG Flags": "bwd_urg_flags",
    "FIN Flag Cnt": "fin_flag_cnt",
    "SYN Flag Cnt": "syn_flag_cnt",
    "RST Flag Cnt": "rst_flag_cnt",
    "PSH Flag Cnt": "psh_flag_cnt",
    "ACK Flag Cnt": "ack_flag_cnt",
    "URG Flag Cnt": "urg_flag_cnt",
    "CWR Flag Cnt": "cwr_flag_count",
    "ECE Flag Cnt": "ece_flag_cnt",
    "Down/Up Ratio": "down_up_ratio",
    "Pkt Size Avg": "pkt_size_avg",
    "Fwd Seg Size Avg": "fwd_seg_size_avg",
    "Bwd Seg Size Avg": "bwd_seg_size_avg",
    "Fwd Byts/b Avg": "fwd_byts_b_avg",
    "Bwd Byts/b Avg": "bwd_byts_b_avg",
    "Fwd Pkts/b Avg": "fwd_pkts_b_avg",
    "Bwd Pkts/b Avg": "bwd_pkts_b_avg",
    "Fwd Blk Rate Avg": "fwd_blk_rate_avg",
    "Bwd Blk Rate Avg": "bwd_blk_rate_avg",
    "Fwd Header Len": "fwd_header_len",
    "Bwd Header Len": "bwd_header_len",
    "Subflow Fwd Pkts": "subflow_fwd_pkts",
    "Subflow Fwd Byts": "subflow_fwd_byts",
    "Subflow Bwd Pkts": "subflow_bwd_pkts",
    "Subflow Bwd Byts": "subflow_bwd_byts",
    "Init Fwd Win Byts": "init_fwd_win_byts",
    "Init Bwd Win Byts": "init_bwd_win_byts",
    "Active Mean": "active_mean",
    "Active Std": "active_std",
    "Active Max": "active_max",
    "Active Min": "active_min",
    "Idle Mean": "idle_mean",
    "Idle Std": "idle_std",
    "Idle Max": "idle_max",
    "Idle Min": "idle_min",
    "Label": "label",
}

for path in input_dir.rglob("*.csv"):
    print(f"Cleaning {path.name}")
    df = pd.read_csv(path, low_memory=False)
    df = df.rename(columns=COLUMN_MAP)
    df = df.drop(columns=cols_to_drop, errors="ignore")
    df = df.fillna(0)
    df.to_csv(output_dir / path.name, index=False)
