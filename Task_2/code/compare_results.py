"""Compare CloudCompare's ASCII export with result."""

from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = PROJECT_ROOT / "Task_2"
OUTPUT_DIR = TASK_DIR / "code" / "output"
PYTHON_FILE = OUTPUT_DIR / "result_python.txt"
CLOUDCOMPARE_FILE = OUTPUT_DIR / "result_cloudcompare.txt"
REPORT_FILE = OUTPUT_DIR / "comparison.txt"


def read_numeric_ascii(path: Path) -> np.ndarray:
    """Read whitespace/comma separated rows, skipping headers and comments."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    rows: list[list[float]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith(("#", "//", "%")):
            continue
        fields = line.replace(",", " ").split()
        try:
            values = [float(field) for field in fields]
        except ValueError:
            # Skip a column-name/header row, if the exporter wrote one.
            continue
        if len(values) < 7:
            raise ValueError(
                f"{path.name}:{line_number}: expected at least 7 numeric columns "
                "in X Y Z R G B ID order."
            )
        rows.append(values[:7])

    if not rows:
        raise ValueError(f"No numeric point rows found in {path}.")
    return np.asarray(rows, dtype=np.float64)


def index_by_id(table: np.ndarray, label: str) -> dict[int, np.ndarray]:
    ids_float = table[:, 6]
    ids = ids_float.astype(np.int64)
    if not np.allclose(ids_float, ids):
        raise ValueError(f"{label}: ID column contains non-integer values.")
    if len(np.unique(ids)) != len(ids):
        raise ValueError(f"{label}: duplicate IDs found.")
    return {int(point_id): row for point_id, row in zip(ids, table)}


def main() -> None:
    python_table = read_numeric_ascii(PYTHON_FILE)
    cc_table = read_numeric_ascii(CLOUDCOMPARE_FILE)
    python_by_id = index_by_id(python_table, "Python output")
    cc_by_id = index_by_id(cc_table, "CloudCompare output")

    python_ids = set(python_by_id)
    cc_ids = set(cc_by_id)
    expected_ids = set(range(1, 501))
    if python_ids != expected_ids:
        raise ValueError("Python output must contain exactly the 500 source IDs (1-500).")
    missing_in_cc = sorted(python_ids - cc_ids)
    extra_in_cc = sorted(cc_ids - python_ids)
    if missing_in_cc or extra_in_cc:
        raise ValueError(
            "ID sets differ. "
            f"Missing from CloudCompare: {missing_in_cc[:10]}; "
            f"extra in CloudCompare: {extra_in_cc[:10]}"
        )

    ordered_ids = sorted(python_ids)
    python_ordered = np.vstack([python_by_id[i] for i in ordered_ids])
    cc_ordered = np.vstack([cc_by_id[i] for i in ordered_ids])

    max_xyz_error = float(np.max(np.abs(python_ordered[:, :3] - cc_ordered[:, :3])))
    rgb_difference = np.abs(
        python_ordered[:, 3:6].astype(np.int16)
        - cc_ordered[:, 3:6].astype(np.int16)
    )
    max_rgb_difference = int(rgb_difference.max())
    differing_channels = int(np.count_nonzero(rgb_difference))
    control_rows = []
    expected_controls = {
        1: (0, 0, 128),
        2: (0, 128, 255),
        3: (128, 255, 255),
        4: (255, 255, 0),
        5: (255, 0, 0),
    }
    for point_id, expected_rgb in expected_controls.items():
        actual_rgb = cc_by_id[point_id][3:6].astype(int)
        control_rows.append(
            f"ID {point_id}: expected {expected_rgb}, CloudCompare {tuple(actual_rgb)}"
        )

    lines = [
        "Topic 2: RGB Levels comparison",
        f"Python points: {len(python_table)}",
        f"CloudCompare points: {len(cc_table)}",
        f"Same ID set: {python_ids == cc_ids}",
        f"Maximum XYZ difference (m): {max_xyz_error:.8g}",
        f"Maximum RGB channel difference: {max_rgb_difference}",
        f"Number of differing RGB channels: {differing_channels}",
        f"Pass RGB tolerance <= 1: {max_rgb_difference <= 1}",
        "Control RGB values (CloudCompare):",
        *control_rows,
        "",
        "Required control mapping: 40->0, 60->0, 110->128, 160->255, 200->255",
        "Clipping examples: 40 and 60 both map to 0; 160 and 200 both map to 255.",
    ]
    report = "\n".join(lines) + "\n"
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(report)
    print(f"Saved comparison report: {REPORT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
