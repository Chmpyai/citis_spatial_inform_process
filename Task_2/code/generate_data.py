"""Create a deterministic synthetic RGB point cloud"""

from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = PROJECT_ROOT / "Task_2"
DATA_DIR = TASK_DIR / "code" / "data"
SOURCE_FILE = DATA_DIR / "source.txt"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)

    # Coordinates are in metres. IDs are unique and remain attached to each point.
    xyz = rng.uniform(0.0, 10.0, size=(500, 3))
    ids = np.arange(1, 501, dtype=np.int64)

    # Put all five required control levels in each channel.
    controls = np.array(
        [
            [40, 60, 110],
            [60, 110, 160],
            [110, 160, 200],
            [160, 200, 40],
            [200, 40, 60],
        ],
        dtype=np.uint8,
    )

    # The remaining colors lie in the main 60-160 range.
    rgb = np.vstack(
        (controls, rng.integers(60, 161, size=(495, 3), dtype=np.uint8))
    )
    source = np.column_stack((xyz, rgb, ids))

    np.savetxt(
        SOURCE_FILE,
        source,
        fmt=("%.6f", "%.6f", "%.6f", "%d", "%d", "%d", "%d"),
        header="X Y Z R G B ID",
        comments="",
    )

    print(f"Created: {SOURCE_FILE.relative_to(PROJECT_ROOT)}")
    print("Points: 500; columns: X Y Z R G B ID")
    print("Control IDs: 1-5")
    print("Open this same source.txt in CloudCompare and Python.")


if __name__ == "__main__":
    main()
