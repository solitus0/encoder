from typing import List
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from encoder.setting import repository, schemas
from encoder.database import get_db
import os
from typing import Optional


router = APIRouter()


@router.post("/api/settings", response_model=schemas.SettingView, status_code=201)
def create_setting(setting: schemas.SettingsCreate, db: Session = Depends(get_db)):
    setting = repository.create_setting(db=db, setting=setting)
    setting.valid = check_path(setting)

    return setting


@router.get("/api/settings/{id}", response_model=schemas.SettingView)
def read_setting(id: int, db: Session = Depends(get_db)):
    db_setting = repository.get_by_id(db, id=id)
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")

    db_setting.valid = check_path(db_setting)

    return db_setting


@router.get("/api/settings", response_model=List[schemas.SettingView])
def read_settings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    settings = repository.get_settings(db, skip=skip, limit=limit)
    for setting in settings:
        setting.valid = check_path(setting)

    return settings


@router.put("/api/settings/{id}", response_model=schemas.SettingView)
def update_setting(
    id: int, setting: schemas.SettingsUpdate, db: Session = Depends(get_db)
):
    db_setting = repository.get_by_id(db, id=id)
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    updated_setting = repository.update_setting(db=db, id=id, setting=setting)
    updated_setting.valid = check_path(updated_setting)

    return updated_setting


@router.delete(
    path="/api/settings/{id}",
    status_code=204,
)
def delete_setting(id: int, db: Session = Depends(get_db)):
    db_setting = repository.get_by_id(db, id=id)
    if db_setting is None:
        raise HTTPException(status_code=404, detail=f"Setting {id} not found")

    repository.delete_setting(db=db, id=id)


def check_path(setting: Optional[schemas.SettingsBase]) -> bool:
    if not setting:
        return False
    return os.path.isdir(setting.value) and os.access(setting.value, os.W_OK)
