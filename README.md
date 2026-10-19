# SmartBridge AI

Computer-vision framework for bridge crack detection, damage classification and
maintenance prioritization (YOLOv8-seg + FastAPI + React).

**Status:** Phases 1–3 complete (skeleton, DB models, auth, bridge CRUD + React UI, ML scripts). See `SmartBridge_AI_Requirements.md` for the full plan.

## Backend setup (macOS, conda)

```bash
conda activate smartbridge          # Python 3.11
cd backend
pip install -r requirements.txt
python seed.py                      # default admin + 3 sample bridges
uvicorn app.main:app --reload
```

- API docs: http://127.0.0.1:8000/docs (use **Authorize** with `admin@smartbridge.com` / `admin123`)
- Health check: http://127.0.0.1:8000/api/health
- Set `SECRET_KEY` in your environment for anything beyond local development.

## Frontend

```bash
cd frontend
npm install
npm run dev                         # http://localhost:5173 (proxies /api to port 8000)
```

Start the backend first. Log in with the seeded admin, or register an engineer/viewer account.
Roles: viewers read only; engineers add/edit bridges; only admins delete bridges.

## ML: dataset, training, evaluation (Apple Silicon / MPS)

All commands run from `backend/` inside `conda activate smartbridge` (`pip install -r requirements.txt` first).

### 1. Download the dataset (DeepCrack)

[DeepCrack](https://github.com/yhlleo/DeepCrack) - 537 crack images with pixel-level binary masks (1 class: `crack`).
Licence: non-commercial research and education only.

```bash
mkdir -p ml/raw && cd ml/raw
git clone --depth 1 https://github.com/yhlleo/DeepCrack.git
mkdir deepcrack && cd deepcrack && unzip ../DeepCrack/dataset/DeepCrack.zip
cd ../../..                         # back to backend/
```

You should now have `ml/raw/deepcrack/{train_img,train_lab,test_img,test_lab}`.

### 2. Convert to YOLO format (70/20/10 split)

```bash
python ml/prepare_dataset.py \
  --source ml/raw/deepcrack/train_img ml/raw/deepcrack/train_lab crack \
  --source ml/raw/deepcrack/test_img  ml/raw/deepcrack/test_lab  crack
```
Writes `ml/dataset/` and `ml/data.yaml`. Add `--clean` to rebuild. Other mask datasets (e.g. CRACK500) work the same way via extra `--source` lines.

### 3. Train

```bash
python ml/train.py --smoke          # ~2 min pipeline check, does not touch weights/best.pt
python ml/train.py                  # full run: yolov8s-seg, 100 epochs, 640px, batch 16
```
The device is picked automatically: `mps` > `cuda` > `cpu`. If you run out of memory, use `--batch 8` or `--model yolov8n-seg.pt`.
If a run is interrupted: `python ml/train.py --resume`. When finished, the best weights are copied to `backend/weights/best.pt` (the previous one is kept as `best_previous.pt`).

### 4. Evaluate

```bash
python ml/evaluate.py               # test split
```
Prints Precision, Recall, F1, mAP@0.5, mAP@0.5:0.95 (mask and box) and pixel IoU. Confusion matrix, PR/F1 curves and `metrics.json` are saved in `ml/results/eval/`.

Only `crack` is trained until a spalling/corrosion dataset is added (class ids 1-3 are already reserved in `data.yaml`).
