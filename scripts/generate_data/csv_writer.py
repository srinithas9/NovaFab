import csv
from pathlib import Path


def write_csv(file_path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    """
    Write a list of dictionaries to a CSV file.
    """

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open(
        mode="w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)