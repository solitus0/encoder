import os
from typing import List, Optional

import aio_pika
from fastapi import Depends, HTTPException, Request, APIRouter
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from . import crud, file_system, presets, schemas
from .database import get_db
from .media_encoder import MediaEncoder
from .scanner import MediaScanner
from .security import decorate_media_with_permissions, has_permission

from .config import (
    RABBITMQ_ENCODE_PROGRESS_QUEUE,
    RABBITMQ_HOST,
    RABBITMQ_USER,
    RABBITMQ_PASS,
)

router = APIRouter()


@router.post("/api/scan", tags=["media"], status_code=204)
def scan(
    db: Session = Depends(get_db),
):
    scanner = MediaScanner(db)
    scanner.scan()


@router.post("/api/directory/validate", tags=["directory"], status_code=204)
def validate(
    command: schemas.ScanCommand,
):
    directory = command.scan_path
    if os.path.isdir(directory):
        return
    else:
        raise HTTPException(status_code=400, detail="Invalid directory path")


@router.get(
    "/api/media",
    response_model=schemas.PaginationResponse,
    tags=["media"],
)
def list_media(
    filter: schemas.PaginationFilter = Depends(),
    db: Session = Depends(get_db),
) -> schemas.PaginationResponse:
    media = crud.get_by_filter(db, filter)

    for item in media.items:
        decorate_media_with_permissions(item)

    return media


@router.get("/api/presets", response_model=list[schemas.Preset], tags=["media"])
def list_presets():
    collection = presets.PresetsCollection()
    presets_list = collection.all()

    return presets_list


@router.post("/api/encodes", tags=["encode"])
def encode(
    command: schemas.EncodeCommand,
    db: Session = Depends(get_db),
):
    media_list = crud.get_by_ids(db, command.media_ids)
    for media in media_list:
        has_permission("ENCODE", media)

    collection = presets.PresetsCollection()
    preset = collection.get(command.preset)
    fileManager = file_system.FileManager(db)
    encoder = MediaEncoder(db, fileManager)
    encoder.batch_encode(media_list, preset)


@router.get("/api/encodes", tags=["encode"])
def list_encodes(
    query: schemas.EncodeQuery = Depends(),
    db: Session = Depends(get_db),
) -> list[schemas.EncodeView]:
    encodes = crud.list_encodes_by_uuid(db, query.media_uuid)

    return encodes


@router.post("/api/settings/", response_model=schemas.SettingsInDB)
def create_setting(setting: schemas.SettingsCreate, db: Session = Depends(get_db)):
    return crud.create_setting(db=db, setting=setting)


@router.get("/api/settings/{setting_key}", response_model=schemas.SettingsInDB)
def read_setting(setting_key: str, db: Session = Depends(get_db)):
    db_setting = crud.get_setting(db, setting_key=setting_key)
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return db_setting


@router.get("/api/settings/", response_model=List[schemas.SettingsInDB])
def read_settings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    settings = crud.get_settings(db, skip=skip, limit=limit)
    return settings


@router.put("/api/settings/{setting_key}", response_model=schemas.SettingsInDB)
def update_setting(
    setting_key: str, setting: schemas.SettingsUpdate, db: Session = Depends(get_db)
):
    db_setting = crud.get_setting(db, setting_key=setting_key)
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return crud.update_setting(db=db, setting_key=setting_key, setting=setting)


@router.delete(
    path="/api/settings/{setting_key}",
    status_code=204,
)
def delete_setting(setting_key: str, db: Session = Depends(get_db)):
    db_setting = crud.get_setting(db, setting_key=setting_key)
    if db_setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")

    crud.delete_setting(db=db, setting_key=setting_key)


async def get_rabbitmq_channel():
    connection = await aio_pika.connect_robust(
        f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}",
        client_properties={"connection_name": "frontend"},
    )
    channel = await connection.channel()
    await channel.declare_queue(RABBITMQ_ENCODE_PROGRESS_QUEUE, durable=False)
    return channel


@router.get("/sse", tags=["encodes"])
async def message_stream(request: Request, channel=Depends(get_rabbitmq_channel)):
    async def event_generator():
        queue = await channel.get_queue(RABBITMQ_ENCODE_PROGRESS_QUEUE)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                if await request.is_disconnected():
                    break

                yield {
                    "event": "progress",
                    "data": message.body.decode(),
                }

                await message.ack()

    return EventSourceResponse(event_generator())


@router.get("/api/permissions", tags=["permissions"])
def get_permissions(db: Session = Depends(get_db)):
    def check_path(path: Optional[schemas.SettingsBase]) -> bool:
        if not path:
            return False
        return os.path.isdir(path.value) and os.access(path.value, os.W_OK)

    scan_path = crud.get_setting(db, schemas.SettingKeyEnum.scan_path)
    temp_path = crud.get_setting(db, schemas.SettingKeyEnum.temp_path)

    is_scan_path_ok = check_path(scan_path)
    is_temp_path_ok = check_path(temp_path)

    return {
        "scan_path": is_scan_path_ok,
        "temp_path": is_temp_path_ok,
        "scan": is_scan_path_ok and is_temp_path_ok,
    }
