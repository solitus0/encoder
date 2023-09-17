import logging

from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from . import schemas
from encoder.media.entity import Media


def get_media(db: Session, media_id: int):
    return db.query(Media).filter(Media.id == media_id).first()


def all(db: Session):
    return db.query(Media).all()


def get_by_uuid(db: Session, uuid: str):
    return db.query(Media).filter(Media.uuid == uuid).first()


def get_by_ids(db: Session, media_ids: list[int]):
    return db.query(Media).filter(Media.uuid.in_(media_ids)).all()


def get_by_filter(
    db: Session, filter: schemas.PaginationFilter
) -> schemas.PaginationResponse:
    query = db.query(Media)

    if filter.operator == "contains":
        value_list = [filter.value]
        if filter.field == "audio_codec":
            query = query.filter(Media.audio_codec.contains(value_list))
        elif filter.field == "video_codec":
            query = query.filter(Media.video_codec.contains(value_list))
        elif filter.field == "subtitle_codec":
            query = query.filter(Media.subtitle_codec.contains(value_list))

        elif filter.field == "file_name":
            query = query.filter(Media.file_name.ilike(f"%{filter.value}%"))
        elif filter.field == "file_path":
            query = query.filter(Media.file_path.ilike(f"%{filter.value}%"))
        elif filter.field == "dimensions":
            query = query.filter(Media.dimensions.ilike(f"%{filter.value}%"))

    total_count = query.count()

    order_by = getattr(Media, filter.orderBy.value)
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
    return db.query(Media).filter(Media.file_path == file_path).first()


def create_media(db: Session, data: schemas.MediaCreate) -> Media:
    db_media = Media(**data.model_dump())
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
