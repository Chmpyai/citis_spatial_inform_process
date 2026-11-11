"""Apply RGB Levels independently in Python and make presentation figures."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = PROJECT_ROOT / "Task_2"
CODE_DIR = TASK_DIR / "code"
DATA_DIR = CODE_DIR / "data"
OUTPUT_DIR = CODE_DIR / "output"
SOURCE_FILE = DATA_DIR / "source.txt"
RESULT_FILE = OUTPUT_DIR / "result_python.txt"
CONTROL_FILE = OUTPUT_DIR / "control_values.csv"
CLOUD_FIGURE = OUTPUT_DIR / "cloud_before_after.png"
HISTOGRAM_FIGURE = OUTPUT_DIR / "histograms_before_after.png"

INPUT_MIN = 60.0
INPUT_MAX = 160.0
OUTPUT_MIN = 0.0
OUTPUT_MAX = 255.0


def stretch_rgb(rgb: np.ndarray) -> np.ndarray:
    """Linearly map input levels to 0-255, clip, round, and return uint8 RGB."""
    rgb_float = np.asarray(rgb, dtype=np.float64)
    scaled = (rgb_float - INPUT_MIN) * (OUTPUT_MAX - OUTPUT_MIN) / (
        INPUT_MAX - INPUT_MIN
    ) + OUTPUT_MIN
    return np.rint(np.clip(scaled, OUTPUT_MIN, OUTPUT_MAX)).astype(np.uint8)


def read_source() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"{SOURCE_FILE} not found. Run generate_data.py first."
        )

    table = np.loadtxt(SOURCE_FILE, skiprows=1)
    if table.shape != (500, 7):
        raise ValueError(f"Expected a 500x7 source table, got {table.shape}.")

    xyz = table[:, :3]
    rgb = table[:, 3:6].astype(np.uint8)
    ids = table[:, 6].astype(np.int64)
    if len(np.unique(ids)) != len(ids):
        raise ValueError("Point IDs in the source file must be unique.")
    return xyz, rgb, ids


def save_cloud_figure(xyz: np.ndarray, before: np.ndarray, after: np.ndarray) -> None:
    fig = plt.figure(figsize=(12, 5))
    for position, colors, title in (
        (1, before, "Original RGB"),
        (2, after, "RGB after Levels"),
    ):
        ax = fig.add_subplot(1, 2, position, projection="3d")
        ax.scatter(
            xyz[:, 0], xyz[:, 1], xyz[:, 2],
            c=colors.astype(np.float64) / 255.0,
            s=12,
            depthshade=False,
        )
        ax.set_title(title)
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_zlabel("Z (m)")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_zlim(0, 10)
        ax.view_init(elev=25, azim=45)
    fig.tight_layout()
    fig.savefig(CLOUD_FIGURE, dpi=180)
    plt.close(fig)


def save_histograms(before: np.ndarray, after: np.ndarray) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    bins = np.arange(-0.5, 256.5, 1)
    channels = ((0, "R", "red"), (1, "G", "green"), (2, "B", "blue"))

    for ax, colors, title in (
        (axes[0], before, "Before Levels"),
        (axes[1], after, "After Levels"),
    ):
        for channel, label, color in channels:
            ax.hist(
                colors[:, channel], bins=bins, histtype="step",
                linewidth=1.5, label=label, color=color,
            )
        ax.set_title(title)
        ax.set_xlabel("Channel value")
        ax.set_xlim(0, 255)
        ax.grid(alpha=0.2)
        ax.legend()
    axes[0].set_ylabel("Number of channel values")
    fig.tight_layout()
    fig.savefig(HISTOGRAM_FIGURE, dpi=180)
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    xyz, rgb_before, ids = read_source()
    rgb_after = stretch_rgb(rgb_before)

    result = np.column_stack((xyz, rgb_after, ids))
    np.savetxt(
        RESULT_FILE,
        result,
        fmt=("%.6f", "%.6f", "%.6f", "%d", "%d", "%d", "%d"),
        header="X Y Z R G B ID",
        comments="",
    )

    control_input = np.array([40, 60, 110, 160, 200], dtype=np.float64)
    control_output = stretch_rgb(control_input)
    np.savetxt(
        CONTROL_FILE,
        np.column_stack((control_input.astype(int), control_output.astype(int))),
        fmt="%d",
        delimiter=",",
        header="input_value,expected_output_value",
        comments="",
    )

    save_cloud_figure(xyz, rgb_before, rgb_after)
    save_histograms(rgb_before, rgb_after)

    print(f"Python result: {RESULT_FILE.relative_to(PROJECT_ROOT)}")
    print(f"Points: {len(ids)}")
    print("Control mapping: 40->0, 60->0, 110->128, 160->255, 200->255")
    print(f"Cloud figure: {CLOUD_FIGURE.relative_to(PROJECT_ROOT)}")
    print(f"Histograms: {HISTOGRAM_FIGURE.relative_to(PROJECT_ROOT)}")
    print("CloudCompare comparison: export to Task_2/code/output/result_cloudcompare.txt")


if __name__ == "__main__":
    main()
