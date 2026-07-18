from pathlib import Path
from typing import cast

import pandas as pd
from sklearn.model_selection import train_test_split
from utils.config import RANDOM_STATE, TRAIN_SIZE

BASE_DIR = Path(__file__).resolve().parent

input_dir = (BASE_DIR / "../../data/clean").resolve()

output_dir = (BASE_DIR / "../../data/processed").resolve()


def split(df: pd.DataFrame, target_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    return cast(
        tuple[pd.DataFrame, pd.DataFrame],
        train_test_split(
            df,
            train_size=TRAIN_SIZE,
            random_state=RANDOM_STATE,
            stratify=df[target_col],
        ),
    )


def main():

    output_dir.mkdir(parents=True, exist_ok=True)
    files = input_dir.glob("*.csv")
    df = pd.concat([pd.read_csv(f) for f in files])
    df = df.fillna(0)
    train, test = split(df, target_col="label")
    train.to_csv(output_dir / "train.csv", index=False)
    test.to_csv(output_dir / "test.csv", index=False)


if __name__ == "__main__":
    main()
