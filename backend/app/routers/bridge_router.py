"""Bridge CRUD. Read: any user. Create/edit: admin + engineer. Delete: admin."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import auth, config, models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/bridges", tags=["bridges"])

can_write = auth.require_roles(config.ROLE_ADMIN, config.ROLE_ENGINEER)
can_delete = auth.require_roles(config.ROLE_ADMIN)

# NOTE: GET /api/bridges/ranking (Phase 5) must be declared before "/{bridge_id}".


def _get_or_404(db: Session, bridge_id: int) -> models.Bridge:
    bridge = db.get(models.Bridge, bridge_id)
    if bridge is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bridge not found")
    return bridge


def _commit(db: Session):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Bridge code already exists")


@router.get("", response_model=list[schemas.BridgeOut])
def list_bridges(db: Session = Depends(get_db), _=Depends(auth.get_current_user)):
    return db.scalars(select(models.Bridge).order_by(models.Bridge.name)).all()


@router.post("", response_model=schemas.BridgeOut, status_code=status.HTTP_201_CREATED)
def create_bridge(data: schemas.BridgeCreate, db: Session = Depends(get_db), _=Depends(can_write)):
    bridge = models.Bridge(**data.model_dump())
    db.add(bridge)
    _commit(db)
    db.refresh(bridge)
    return bridge


@router.get("/{bridge_id}", response_model=schemas.BridgeOut)
def get_bridge(bridge_id: int, db: Session = Depends(get_db), _=Depends(auth.get_current_user)):
    return _get_or_404(db, bridge_id)


@router.put("/{bridge_id}", response_model=schemas.BridgeOut)
def update_bridge(
    bridge_id: int, data: schemas.BridgeUpdate, db: Session = Depends(get_db), _=Depends(can_write)
):
    bridge = _get_or_404(db, bridge_id)
    for field, value in data.model_dump().items():
        setattr(bridge, field, value)
    _commit(db)
    db.refresh(bridge)
    return bridge


@router.delete("/{bridge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bridge(bridge_id: int, db: Session = Depends(get_db), _=Depends(can_delete)):
    db.delete(_get_or_404(db, bridge_id))  # cascades to inspections/images/defects
    db.commit()
