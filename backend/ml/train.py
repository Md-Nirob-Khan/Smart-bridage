"""Train YOLOv8-seg on the prepared dataset and publish the best weights.

    python ml/train.py                       # spec defaults: yolov8s-seg, 100 epochs, 640px, batch 16
    python ml/train.py --smoke               # ~1 minute pipeline check, does NOT touch weights/best.pt
Device is chosen automatically: mps (Apple Silicon) > cuda > cpu.
"""
import os

# Must be set before torch is imported: unsupported MPS ops fall back to CPU instead of crashing.
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

import argparse
import shutil

from common import BEST_WEIGHTS, PRETRAINED_DIR, RUNS_DIR, pick_device, resolved_data_yaml


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="yolov8s-seg.pt", help="e.g. yolov8n-seg.pt (faster) or yolov8s-seg.pt")
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=16, help="lower to 8 or 4 if you run out of memory")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--patience", type=int, default=30, help="early stop after N epochs without improvement")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--fraction", type=float, default=1.0, help="use only this fraction of the train set")
    ap.add_argument("--name", default="smartbridge")
    ap.add_argument("--resume", action="store_true", help="resume the last interrupted run of --name")
    ap.add_argument("--no-export", action="store_true", help="do not copy best.pt to backend/weights/")
    ap.add_argument("--smoke", action="store_true", help="1 epoch, 10%% of data, yolov8n-seg, no export")
    args = ap.parse_args()

    if args.smoke:
        args.model, args.epochs, args.fraction, args.batch = "yolov8n-seg.pt", 1, 0.1, 8
        args.name, args.no_export, args.patience = "smoke", True, 100

    from ultralytics import YOLO

    device = pick_device(args.device)
    data = resolved_data_yaml()
    PRETRAINED_DIR.mkdir(exist_ok=True)
    os.chdir(PRETRAINED_DIR)  # pretrained *.pt files get downloaded into the current folder
    print(f"Device: {device} | model: {args.model} | data: {data}")

    last = RUNS_DIR / args.name / "weights" / "last.pt"
    model = YOLO(str(last) if args.resume else args.model)
    model.train(
        data=str(data),
        epochs=args.epochs, imgsz=args.imgsz, batch=args.batch, workers=args.workers,
        patience=args.patience, device=device, fraction=args.fraction,
        project=str(RUNS_DIR), name=args.name, exist_ok=True, resume=args.resume,
        # Augmentation (SRS 8.3): flips, rotation, brightness; mosaic/scale are YOLO defaults.
        # Blur is applied automatically if `albumentations` is installed (pip install albumentations).
        fliplr=0.5, flipud=0.5, degrees=10, hsv_v=0.4, hsv_s=0.5, scale=0.5, mosaic=1.0,
        plots=True,
    )

    best = RUNS_DIR / args.name / "weights" / "best.pt"
    if not best.exists():
        raise SystemExit(f"Training finished but {best} was not found.")
    print(f"\nBest weights: {best}")
    if args.no_export:
        return
    BEST_WEIGHTS.parent.mkdir(exist_ok=True)
    if BEST_WEIGHTS.exists():
        shutil.copy2(BEST_WEIGHTS, BEST_WEIGHTS.with_name("best_previous.pt"))  # keep one backup
    shutil.copy2(best, BEST_WEIGHTS)
    print(f"Copied to {BEST_WEIGHTS}")


if __name__ == "__main__":
    main()
