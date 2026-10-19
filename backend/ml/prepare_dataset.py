"""Convert binary-mask crack datasets into the YOLOv8 segmentation format.

Each --source is a folder of images + a folder of binary masks (white = defect).
Image/mask pairs are matched by file name (stem). All sources are pooled, shuffled
and split 70/20/10 into train/val/test. Output goes to ml/dataset/.

Example (DeepCrack, which ships train_img/train_lab/test_img/test_lab):
    python ml/prepare_dataset.py \
        --source RAW/train_img RAW/train_lab crack \
        --source RAW/test_img  RAW/test_lab  crack
"""
import argparse
import random
import shutil
from pathlib import Path

import cv2
import numpy as np
import yaml

from common import CLASS_NAMES, DATA_YAML, DATASET_DIR

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
MASK_SUFFIXES = ("", "_mask", "_gt", "_label", "_lab", "-mask")  # tolerated name variants


def find_mask(mask_dir: Path, stem: str) -> Path | None:
    for suffix in MASK_SUFFIXES:
        for ext in IMG_EXT:
            p = mask_dir / f"{stem}{suffix}{ext}"
            if p.exists():
                return p
    return None


def resize_pair(img: np.ndarray, mask: np.ndarray, max_size: int):
    """Downscale so the longest side <= max_size (huge photos are slow to train on)."""
    h, w = img.shape[:2]
    scale = max_size / max(h, w)
    if scale >= 1:
        return img, mask
    size = (round(w * scale), round(h * scale))
    img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    # INTER_AREA keeps 1-2 px wide cracks alive; nearest would often erase them.
    mask = cv2.resize(mask, size, interpolation=cv2.INTER_AREA)
    return img, mask


def mask_to_polygons(mask: np.ndarray, min_len: float, epsilon: float):
    """Binary mask -> list of normalized polygons [[x1,y1,x2,y2,...], ...]."""
    h, w = mask.shape
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polys = []
    for c in contours:
        if cv2.arcLength(c, True) < min_len:
            continue  # speckle noise
        approx = cv2.approxPolyDP(c, epsilon, True)
        if len(approx) < 3:
            approx = c  # very thin crack: keep the raw contour
        if len(approx) < 3:
            continue
        pts = approx.reshape(-1, 2).astype(np.float64)
        pts[:, 0] /= w
        pts[:, 1] /= h
        polys.append(np.clip(pts, 0, 1).flatten())
    return polys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", nargs=3, action="append", required=True,
                    metavar=("IMAGES_DIR", "MASKS_DIR", "CLASS"),
                    help=f"repeatable; CLASS is one of {CLASS_NAMES}")
    ap.add_argument("--max-size", type=int, default=1024, help="longest image side after resize")
    ap.add_argument("--min-len", type=float, default=16.0, help="drop contours shorter than this (px)")
    ap.add_argument("--epsilon", type=float, default=1.0, help="polygon simplification tolerance (px)")
    ap.add_argument("--split", nargs=3, type=float, default=(0.7, 0.2, 0.1), metavar=("TRAIN", "VAL", "TEST"))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--clean", action="store_true", help="delete an existing ml/dataset first")
    args = ap.parse_args()

    if abs(sum(args.split) - 1) > 1e-6:
        raise SystemExit("--split must sum to 1")
    if DATASET_DIR.exists():
        if not args.clean:
            raise SystemExit(f"{DATASET_DIR} already exists. Re-run with --clean to rebuild it.")
        shutil.rmtree(DATASET_DIR)

    # ---- collect (image, mask, class_id) triples from every source ----
    items = []
    for idx, (img_dir, mask_dir, cls) in enumerate(args.source):
        if cls not in CLASS_NAMES:
            raise SystemExit(f"Unknown class '{cls}'. Use one of {CLASS_NAMES}")
        img_dir, mask_dir = Path(img_dir), Path(mask_dir)
        for d in (img_dir, mask_dir):
            if not d.is_dir():
                raise SystemExit(f"Not a folder: {d}")
        found = missing = 0
        for img in sorted(img_dir.iterdir()):
            if img.suffix.lower() not in IMG_EXT:
                continue
            m = find_mask(mask_dir, img.stem)
            if m is None:
                missing += 1
                continue
            items.append((idx, img, m, CLASS_NAMES.index(cls)))
            found += 1
        print(f"source {idx}: {found} pairs, {missing} images without mask ({img_dir})")
    if not items:
        raise SystemExit("No image/mask pairs found - check the folders and file names.")

    random.Random(args.seed).shuffle(items)
    n = len(items)
    n_train = round(n * args.split[0])
    n_val = round(n * args.split[1])
    splits = {"train": items[:n_train], "val": items[n_train:n_train + n_val], "test": items[n_train + n_val:]}

    # ---- convert ----
    stats = {}
    for name, rows in splits.items():
        (DATASET_DIR / "images" / name).mkdir(parents=True)
        (DATASET_DIR / "labels" / name).mkdir(parents=True)
        n_poly = n_empty = 0
        for src_idx, img_p, mask_p, cls_id in rows:
            img = cv2.imread(str(img_p), cv2.IMREAD_COLOR)
            mask = cv2.imread(str(mask_p), cv2.IMREAD_GRAYSCALE)
            if img is None or mask is None:
                print(f"  skip unreadable: {img_p.name}")
                continue
            if mask.shape != img.shape[:2]:
                mask = cv2.resize(mask, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
            # Works for 0/255 and 0/1 masks alike.
            binary = ((mask > 0) * 255).astype(np.uint8)
            img, binary = resize_pair(img, binary, args.max_size)
            binary = (binary >= 64).astype(np.uint8) * 255

            stem = f"s{src_idx}_{img_p.stem}"
            cv2.imwrite(str(DATASET_DIR / "images" / name / f"{stem}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            polys = mask_to_polygons(binary, args.min_len, args.epsilon)
            lines = [f"{cls_id} " + " ".join(f"{v:.6f}" for v in p) for p in polys]
            # An empty label file = background-only image (useful negative sample).
            (DATASET_DIR / "labels" / name / f"{stem}.txt").write_text("\n".join(lines))
            n_poly += len(polys)
            n_empty += not polys
        stats[name] = (len(rows), n_poly, n_empty)

    DATA_YAML.write_text(yaml.safe_dump({
        "path": "dataset",  # relative; common.resolved_data_yaml() makes it absolute at run time
        "train": "images/train", "val": "images/val", "test": "images/test",
        "names": dict(enumerate(CLASS_NAMES)),
    }, sort_keys=False))

    print(f"\nWrote {DATASET_DIR} and {DATA_YAML}")
    for name, (imgs, polys, empty) in stats.items():
        print(f"  {name:5s}: {imgs:4d} images, {polys:5d} polygons, {empty} without labels")


if __name__ == "__main__":
    main()
