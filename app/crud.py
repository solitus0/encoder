from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from . import models, schemas
from .models import Media


def get_media(db: Session, media_id: int):
    return db.query(models.Media).filter(models.Media.id == media_id).first()


def get_medias(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Media).offset(offset).limit(limit).all()


def get_by_file_path(db: Session, file_path: str):
    return db.query(models.Media).filter(models.Media.file_path == file_path).first()


def create_media(db: Session, data: schemas.MediaCreate) -> Media:
    db_media = models.Media(**data.model_dump())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)

    return db_media


def update_media(db: Session, media: Media, data: schemas.Media) -> Media:
    media.update(data.model_dump())
    db.commit()
    db.refresh(media)

    return media


def should_update(model: BaseModel, database_model):
    # Get the column names from the SQLAlchemy model
    column_names = [
        column.key for column in inspect(database_model).mapper.column_attrs
    ]

    # Get the attributes of the Pydantic schema object
    schema_attributes = set(model.__fields__.keys())

    # Compare the sets of column names and schema attributes
    if not schema_attributes.issubset(column_names):
        raise ValueError("Pydantic schema attributes do not match the database fields.")

    # Get the values of the Pydantic schema object attributes
    schema_values = {attr: getattr(model, attr) for attr in schema_attributes}

    # Get the values of the SQLAlchemy model object attributes
    model_values = {attr: getattr(database_model, attr) for attr in schema_attributes}

    # Compare the values of the Pydantic schema object and the SQLAlchemy model object
    return schema_values != model_values
