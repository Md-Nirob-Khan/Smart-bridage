"""Central settings: paths, security, and all tunable thresholds/weights.

Values that the SRS says must be editable (severity rules, score weights,
priority bands) live here so nothing is hard-coded in the services.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/

# ---- Paths ----
UPLOAD_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
WEIGHTS_DIR = BASE_DIR / "weights"
MODEL_PATH = WEIGHTS_DIR / "best.pt"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'smartbridge.db'}")

# ---- Security ----
# Override SECRET_KEY via environment in any real deployment.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ---- Web ----
CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]  # Vite dev server
MAX_UPLOAD_MB = 10

# ---- Roles ----
ROLE_ADMIN = "admin"
ROLE_ENGINEER = "engineer"
ROLE_VIEWER = "viewer"
ALL_ROLES = (ROLE_ADMIN, ROLE_ENGINEER, ROLE_VIEWER)

# ---- Detection (used from Phase 4) ----
CONF_THRESHOLD = 0.4
DEVICE_PREFERENCE = ("mps", "cuda", "cpu")  # first available wins (MPS on Apple Silicon)

# ---- Severity rules for cracks (FR6) ----
SEVERITY_MM = {"low_max": 0.3, "medium_max": 1.0}   # < 0.3 low, 0.3-1.0 medium, > 1.0 high
SEVERITY_PX = {"low_max": 3, "medium_max": 8}       # used when no mm scale is given
LENGTH_ESCALATION_RATIO = 0.30                      # length > 30% of image diagonal -> +1 level
ALWAYS_HIGH_TYPES = ("spalling", "corrosion")

# ---- Damage score weights (FR7) ----
DAMAGE_WEIGHTS = {"severity": 0.40, "density": 0.25, "count": 0.20, "type": 0.15}

# ---- Risk score weights (FR7) ----
RISK_WEIGHTS = {"damage": 0.70, "age": 0.15, "traffic": 0.15}

# ---- Priority bands (FR7): minimum risk score for each level ----
PRIORITY_BANDS = {"High": 70, "Medium": 40, "Low": 0}
RECOMMENDATIONS = {
    "High": "Immediate repair / restrict load, inspect within 1 week.",
    "Medium": "Schedule repair within 1-3 months.",
    "Low": "Routine monitoring, re-inspect within 6-12 months.",
}
