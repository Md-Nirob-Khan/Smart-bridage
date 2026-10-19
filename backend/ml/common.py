"""Shared constants/helpers for the ML scripts (kept independent of the web app)."""
from pathlib import Path

import yaml

ML_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ML_DIR.parent
DATASET_DIR = ML_DIR / "dataset"
DATA_YAML = ML_DIR / "data.yaml"
RUNS_DIR = ML_DIR / "runs"
RESULTS_DIR = ML_DIR / "results"
PRETRAINED_DIR = ML_DIR / "pretrained"
BEST_WEIGHTS = BACKEND_DIR / "weights" / "best.pt"

# Class order is fixed: the ids are baked into the trained weights and the dataset labels.
CLASS_NAMES = ["crack", "spalling", "corrosion", "efflorescence"]


def pick_device(requested: str = "auto") -> str:
    """'auto' -> mps (Apple Silicon) if available, else cuda, else cpu."""
    if requested != "auto":
        return requested
    import torch

    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "0"
    return "cpu"


def resolved_data_yaml() -> Path:
    """Write a copy of data.yaml with an absolute dataset path and return it.

    Ultralytics resolves a relative `path:` against its own datasets dir, not the
    yaml's folder, so we always hand it an absolute path.
    """
    if not DATASET_DIR.exists():
        raise SystemExit(
            f"Dataset not found at {DATASET_DIR}.\nRun ml/prepare_dataset.py first (see README)."
        )
    cfg = yaml.safe_load(DATA_YAML.read_text())
    cfg["path"] = str(DATASET_DIR.resolve())
    out = DATASET_DIR / "data.resolved.yaml"
    out.write_text(yaml.safe_dump(cfg, sort_keys=False))
    return out
