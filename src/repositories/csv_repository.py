from pathlib import Path

import pandas as pd


BASE_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
)


class CSVRepository:
    def __init__(self, base_dir: Path = BASE_DIR):
        self.base_dir = base_dir

    def read(self, filename: str) -> pd.DataFrame:
        path = self.base_dir / filename

        if not path.exists():
            raise FileNotFoundError(
                f"{filename} not found at {path}"
            )

        return pd.read_csv(path)

    def write(
        self,
        filename: str,
        df: pd.DataFrame,
    ) -> None:
        self.base_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = self.base_dir / filename

        df.to_csv(
            path,
            index=False,
        )

    def exists(self, filename: str) -> bool:
        return (
            self.base_dir / filename
        ).exists()