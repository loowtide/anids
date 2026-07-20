import hashlib
import json
import os
import shutil
from datetime import datetime

import pandas as pd

JSON_SAVE = "../cols_to_drop.json"
DATA_DIR = "../../data/processed/"
BACKUP_DIR = os.path.join(
    DATA_DIR, "backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
)


def find_duplicate_column(df):
    hash_col = {}
    for col in df.columns:
        col_hash = hashlib.sha256(df[col].to_numpy().tobytes()).hexdigest()
        hash_col.setdefault(col_hash, []).append(col)

    duplicate = [cols for cols in hash_col.values() if len(cols) > 1]
    return duplicate


def save_dup_cols():
    dfs = ["train.csv", "test.csv"]
    cols_to_drop = {}
    loaded = {}
    for file in dfs:
        path = os.path.join(DATA_DIR, file)
        df = pd.read_csv(path)
        df["label"] = df["label"].str.strip().str.lower()
        dup_groups = find_duplicate_column(df)
        cols_to_drop[file] = {col for group in dup_groups for col in group[1:]}
        loaded[file] = df

    union = set.union(*cols_to_drop.values())  # cols to remove
    with open(JSON_SAVE, "w") as f:
        json.dump(sorted(union), f, indent=2)
        print("Columns to drop saved!")
    return loaded


def apply_drops(df):
    with open(JSON_SAVE, "r") as f:
        cols_to_drop = json.load(f)

    df = df.drop(columns=cols_to_drop, errors="ignore")
    df = df.fillna(0)
    return df


def main():
    dfs = ["train.csv", "test.csv"]

    # ------ Backup original csv ------------
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for file in dfs:
        src = os.path.join(DATA_DIR, file)
        dst = os.path.join(BACKUP_DIR, file)
        shutil.copy2(src, dst)
    print(f"Backed file : {BACKUP_DIR}")

    loaded = save_dup_cols()

    for file in dfs:
        path = os.path.join(DATA_DIR, file)
        df = apply_drops(loaded[file])
        df.to_csv(path, index=False)
    print("Columns dropped!")
    print("All done!!")


if __name__ == "__main__":
    main()
