from sqlalchemy.orm import Session

from . import entity
from . import schemas


def create_setting(db: Session, setting: schemas.SettingsCreate):
    db_setting = entity.Settings(**setting.model_dump())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting


def get_setting(db: Session, id: int) -> entity.Settings:
    return db.query(entity.Settings).filter(entity.Settings.id == id).first()


def get_settings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(entity.Settings).offset(skip).limit(limit).all()


def update_setting(db: Session, id: int, setting: schemas.SettingsUpdate):
    db_setting = db.query(entity.Settings).filter(entity.Settings.id == id).first()
    for key, value in setting.model_dump().items():
        setattr(db_setting, key, value)
    db.commit()
    db.refresh(db_setting)
    return db_setting


def delete_setting(db: Session, id: int):
    db_setting = db.query(entity.Settings).filter(entity.Settings.id == id).first()
    db.delete(db_setting)
    db.commit()
