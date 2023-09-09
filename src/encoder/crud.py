import logging

from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from . import models, schemas
from .models import Media


def get_media(db: Session, media_id: int):
    return db.query(models.Media).filter(models.Media.id == media_id).first()


def all(db: Session):
    return db.query(models.Media).all()


def get_by_uuid(db: Session, uuid: str):
    return db.query(models.Media).filter(models.Media.uuid == uuid).first()


def get_by_ids(db: Session, media_ids: list[int]):
    return db.query(models.Media).filter(models.Media.uuid.in_(media_ids)).all()


def get_by_filter(
    db: Session, filter: schemas.PaginationFilter
) -> schemas.PaginationResponse:
    query = db.query(models.Media)

    if filter.operator == "contains":
        value_list = [filter.value]
        if filter.field == "audio_codec":
            query = query.filter(models.Media.audio_codec.contains(value_list))
        elif filter.field == "video_codec":
            query = query.filter(models.Media.video_codec.contains(value_list))
        elif filter.field == "subtitle_codec":
            query = query.filter(models.Media.subtitle_codec.contains(value_list))

        elif filter.field == "file_name":
            query = query.filter(models.Media.file_name.ilike(f"%{filter.value}%"))
        elif filter.field == "file_path":
            query = query.filter(models.Media.file_path.ilike(f"%{filter.value}%"))
        elif filter.field == "dimensions":
            query = query.filter(models.Media.dimensions.ilike(f"%{filter.value}%"))

    total_count = query.count()

    order_by = getattr(models.Media, filter.orderBy.value)
    order_direction = getattr(order_by, filter.orderDirection.value)

    paginated_query = (
        query.order_by(order_direction())
        .offset((filter.page - 1) * filter.pageSize)
        .limit(filter.pageSize)
    )

    results = paginated_query.all()

    response = schemas.PaginationResponse(
        totalItems=total_count,
        currentPage=filter.page,
        pageSize=filter.pageSize,
        items=results,
    )

    return response


def get_by_file_path(db: Session, file_path: str):
    return db.query(models.Media).filter(models.Media.file_path == file_path).first()


def create_media(db: Session, data: schemas.MediaCreate) -> Media:
    db_media = models.Media(**data.model_dump())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)

    return db_media


def update_media(db: Session, media: Media, data: schemas.MediaCreate) -> Media:
    for key, value in data.model_dump().items():
        if getattr(media, key) != value:
            logging.info(f"Updating {key} from {getattr(media, key)} to {value}")
            setattr(media, key, value)

    db.commit()
    db.refresh(media)

    return media


def initialize_encode(db: Session, data: schemas.InitializeEncode) -> models.Encode:
    db_encode = models.Encode(**data.model_dump())
    db.add(db_encode)
    db.commit()
    db.refresh(db_encode)

    return db_encode


def get_encode_by_uuid(db: Session, media_uuid: str) -> models.Encode:
    return (
        db.query(models.Encode).filter(models.Encode.media_uuid == media_uuid).first()
    )


def get_encode_by_uuid_and_status(
    db: Session, media_uuid: str, status: str = "queued"
) -> models.Encode:
    return (
        db.query(models.Encode)
        .filter(models.Encode.media_uuid == media_uuid, models.Encode.status == status)
        .first()
    )


def update_encode(
    db: Session, encode: models.Encode, data: schemas.FinishEncode
) -> models.Encode:
    for key, value in data.model_dump().items():
        setattr(encode, key, value)

    db.commit()
    db.refresh(encode)

    return encode


def should_update(model: BaseModel, database_model):
    column_names = [
        column.key for column in inspect(database_model).mapper.column_attrs
    ]

    schema_attributes = set(model.__fields__.keys())
    if not schema_attributes.issubset(column_names):
        raise ValueError("Pydantic schema attributes do not match the database fields.")

    schema_values = {
        attr: getattr(model, attr) for attr in schema_attributes if attr not in ["uuid"]
    }

    model_values = {
        attr: getattr(database_model, attr)
        for attr in schema_attributes
        if attr not in ["uuid"]
    }

    return schema_values != model_values


def list_encodes_by_uuid(db: Session, uuid: str):
    return db.query(models.Encode).filter(models.Encode.media_uuid == uuid).all()


def create_setting(db: Session, setting: schemas.SettingsCreate):
    db_setting = models.Settings(**setting.model_dump())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting


def get_setting(db: Session, setting_key: str) -> models.Settings:
    return db.query(models.Settings).filter(models.Settings.key == setting_key).first()


def get_settings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Settings).offset(skip).limit(limit).all()


def update_setting(db: Session, setting_key: str, setting: schemas.SettingsUpdate):
    db_setting = (
        db.query(models.Settings).filter(models.Settings.key == setting_key).first()
    )
    for key, value in setting.model_dump().items():
        setattr(db_setting, key, value)
    db.commit()
    db.refresh(db_setting)
    return db_setting


def delete_setting(db: Session, setting_key: str):
    db_setting = (
        db.query(models.Settings).filter(models.Settings.key == setting_key).first()
    )
    db.delete(db_setting)
    db.commit()
