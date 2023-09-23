from typing import List
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from encoder.setting import repository, schemas
from encoder.database import get_db


router = APIRouter()


@router.post("/api/settings/", response_model=schemas.SettingsInDB, status_code=201)
def create_setting(setting: schemas.SettingsCreate, db: Session = Depends(get_db)):
    return repository.create_setting(db=db, setting=setting)


@router.get("/api/settings/{id}", response_model=schemas.SettingsInDB)
def read_setting(id: int, db: Session = Depends(get_db)):
    db_setting = repository.get_setting(db, id=id)
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return db_setting


@router.get("/api/settings/", response_model=List[schemas.SettingsInDB])
def read_settings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    settings = repository.get_settings(db, skip=skip, limit=limit)
    return settings


@router.put("/api/settings/{id}", response_model=schemas.SettingsInDB)
def update_setting(
    id: int, setting: schemas.SettingsUpdate, db: Session = Depends(get_db)
):
    db_setting = repository.get_setting(db, id=id)
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return repository.update_setting(db=db, id=id, setting=setting)


@router.delete(
    path="/api/settings/{id}",
    status_code=204,
)
def delete_setting(id: int, db: Session = Depends(get_db)):
    db_setting = repository.get_setting(db, id=id)
    if db_setting is None:
        raise HTTPException(status_code=404, detail=f"Setting {id} not found")

    repository.delete_setting(db=db, id=id)
