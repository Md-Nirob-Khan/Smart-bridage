"""Create tables, a default admin and 3 sample bridges (safe to re-run).

Run from backend/:  python seed.py
"""
from sqlalchemy import select

from app import auth, models
from app.database import Base, SessionLocal, engine

SAMPLE_BRIDGES = [
    dict(code="BR-001", name="Padma River Approach Bridge", location="Mawa, Munshiganj",
         latitude=23.4607, longitude=90.2650, length_m=420, construction_year=1998,
         bridge_type="RCC", daily_traffic=18000, notes="Sample bridge"),
    dict(code="BR-002", name="Karnaphuli Steel Bridge", location="Chattogram",
         latitude=22.3475, longitude=91.8123, length_m=250, construction_year=1975,
         bridge_type="Steel", daily_traffic=32000, notes="Sample bridge"),
    dict(code="BR-003", name="Dhaleshwari Footbridge", location="Savar, Dhaka",
         latitude=23.8433, longitude=90.2570, length_m=90, construction_year=2015,
         bridge_type="Prestressed", daily_traffic=3000, notes="Sample bridge"),
]


def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.scalar(select(models.User).where(models.User.email == "admin@smartbridge.com")):
            db.add(models.User(name="Admin", email="admin@smartbridge.com",
                               password_hash=auth.hash_password("admin123"), role="admin"))
            print("Created admin: admin@smartbridge.com / admin123")
        for b in SAMPLE_BRIDGES:
            if not db.scalar(select(models.Bridge).where(models.Bridge.code == b["code"])):
                db.add(models.Bridge(**b))
                print(f"Created bridge {b['code']}")
        db.commit()


if __name__ == "__main__":
    main()
