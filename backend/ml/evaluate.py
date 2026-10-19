"""Evaluate trained weights: Precision, Recall, F1, mAP@0.5, mAP@0.5:0.95, IoU, confusion matrix.

    python ml/evaluate.py                      # test split, backend/weights/best.pt
    python ml/evaluate.py --split val
Outputs (plots + metrics.json) are saved in ml/results/<name>/ for the thesis.
"""
import os

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

import argparse
import json

import cv2
import numpy as np

from common import BEST_WEIGHTS, CLASS_NAMES, DATASET_DIR, RESULTS_DIR, pick_device, resolved_data_yaml


def gt_mask(label_file, h, w):
    """Rasterize a YOLO-seg label file into a class-agnostic binary mask."""
    m = np.zeros((h, w), np.uint8)
    if label_file.exists():
        for line in label_file.read_text().split("\n"):
            vals = line.split()
            if len(vals) < 7:
                continue
            pts = np.array(vals[1:], dtype=np.float64).reshape(-1, 2) * [w, h]
            cv2.fillPoly(m, [pts.round().astype(np.int32)], 1)
    return m


def pred_mask(result, h, w):
    m = np.zeros((h, w), np.uint8)
    if result.masks is not None:
        for poly in result.masks.xy:
            if len(poly) >= 3:
                cv2.fillPoly(m, [np.round(poly).astype(np.int32)], 1)
    return m


def segmentation_iou(model, split, imgsz, conf, device):
    """Pixel IoU of 'any defect' (class-agnostic) between predictions and labels."""
    img_dir = DATASET_DIR / "images" / split
    lbl_dir = DATASET_DIR / "labels" / split
    inter = union = 0
    per_image = []
    for res in model.predict(str(img_dir), imgsz=imgsz, conf=conf, device=device, stream=True, verbose=False):
        h, w = res.orig_shape
        gt = gt_mask(lbl_dir / (os.path.splitext(os.path.basename(res.path))[0] + ".txt"), h, w)
        pr = pred_mask(res, h, w)
        i, u = int((gt & pr).sum()), int((gt | pr).sum())
        inter, union = inter + i, union + u
        if gt.any():  # per-image mean only over images that actually contain a defect
            per_image.append(i / u)
    return {
        "iou_global": inter / union if union else float("nan"),
        "iou_mean_per_image": float(np.mean(per_image)) if per_image else float("nan"),
        "images_with_defects": len(per_image),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--weights", default=str(BEST_WEIGHTS))
    ap.add_argument("--split", default="test", choices=["train", "val", "test"])
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--iou-conf", type=float, default=0.4, help="confidence used for the IoU calculation")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--name", default="eval")
    args = ap.parse_args()

    from ultralytics import YOLO

    if not os.path.exists(args.weights):
        raise SystemExit(f"Weights not found: {args.weights}\nModel not trained yet - run ml/train.py")
    device = pick_device(args.device)
    model = YOLO(args.weights)

    # Standard detection/segmentation metrics + confusion matrix and PR/F1 curves (saved as PNGs).
    m = model.val(data=str(resolved_data_yaml()), split=args.split, imgsz=args.imgsz, device=device,
                  plots=True, project=str(RESULTS_DIR), name=args.name, exist_ok=True, verbose=False)

    def block(x):  # x = m.box or m.seg
        p, r = float(x.mp), float(x.mr)
        return {"precision": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else 0.0,
                "mAP50": float(x.map50), "mAP50_95": float(x.map)}

    out = {"weights": args.weights, "split": args.split, "classes": CLASS_NAMES,
           "mask": block(m.seg), "box": block(m.box)}
    out.update(segmentation_iou(model, args.split, args.imgsz, args.iou_conf, device))

    save_dir = RESULTS_DIR / args.name
    (save_dir / "metrics.json").write_text(json.dumps(out, indent=2))

    print("\n=== Results on", args.split, "split ===")
    for kind in ("mask", "box"):
        b = out[kind]
        print(f"{kind:4s}: P={b['precision']:.3f} R={b['recall']:.3f} F1={b['f1']:.3f} "
              f"mAP50={b['mAP50']:.3f} mAP50-95={b['mAP50_95']:.3f}")
    print(f"IoU : global={out['iou_global']:.3f} mean/image={out['iou_mean_per_image']:.3f} "
          f"({out['images_with_defects']} images with defects, conf>={args.iou_conf})")
    print(f"Plots + metrics.json saved in {save_dir}")


if __name__ == "__main__":
    main()
