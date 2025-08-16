import csv
import re
from pathlib import Path

import numpy as np


def keep_only_alpha_numerical(content: str) -> str:
    return re.sub(r"[^0-9a-zA-B]", "", content)


def save_csv_with_columns(array: np.ndarray,
                          columns: list[str],
                          output_csv: Path) -> None:
    with open(output_csv, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(columns)
        writer.writerows(array)
