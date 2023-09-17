from sqlalchemy.orm import Session

from encoder.encode import schemas as encode_schemas
from encoder.encode.entity import Encode


def initialize_encode(db: Session, data: encode_schemas.InitializeEncode) -> Encode:
    db_encode = Encode(**data.model_dump())
    db.add(db_encode)
    db.commit()
    db.refresh(db_encode)

    return db_encode


def get_encode_by_uuid(db: Session, media_uuid: str) -> Encode:
    return db.query(Encode).filter(Encode.media_uuid == media_uuid).first()


def get_encode_by_uuid_and_status(
    db: Session, media_uuid: str, status: str = "queued"
) -> Encode:
    return (
        db.query(Encode)
        .filter(Encode.media_uuid == media_uuid, Encode.status == status)
        .first()
    )


def update_encode(
    db: Session, encode: Encode, data: encode_schemas.FinishEncode
) -> Encode:
    for key, value in data.model_dump().items():
        setattr(encode, key, value)

    db.commit()
    db.refresh(encode)

    return encode


def list_encodes_by_uuid(db: Session, uuid: str):
    return db.query(Encode).filter(Encode.media_uuid == uuid).all()
