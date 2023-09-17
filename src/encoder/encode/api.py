import aio_pika
from fastapi import Depends, Request, APIRouter
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from encoder.preset import presets
from encoder.media import file_system
from encoder.encode import repository
from encoder.media import repository as media_repository
from encoder.database import get_db
from encoder.encode.schemas import EncodeCommand, EncodeQuery, EncodeView
from encoder.encode.enqueuer import EncodeEnqueuer
from encoder.permissions.security import has_permission

from encoder.config import (
    RABBITMQ_ENCODE_PROGRESS_QUEUE,
    RABBITMQ_HOST,
    RABBITMQ_USER,
    RABBITMQ_PASS,
)

router = APIRouter()


async def get_rabbitmq_channel():
    connection = await aio_pika.connect_robust(
        f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}",
        client_properties={"connection_name": "frontend"},
    )
    channel = await connection.channel()
    await channel.declare_queue(RABBITMQ_ENCODE_PROGRESS_QUEUE, durable=False)
    return channel


@router.post("/api/encodes", tags=["encode"])
def encode(
    command: EncodeCommand,
    db: Session = Depends(get_db),
):
    media_list = media_repository.get_by_ids(db, command.media_ids)
    for media in media_list:
        has_permission("ENCODE", media)

    collection = presets.PresetsCollection()
    preset = collection.get(command.preset)
    fileManager = file_system.FileManager(db)
    encoder = EncodeEnqueuer(db, fileManager)
    encoder.enqueue_for_processing(media_list, preset)


@router.get("/api/encodes", tags=["encode"])
def list_encodes(
    query: EncodeQuery = Depends(),
    db: Session = Depends(get_db),
) -> list[EncodeView]:
    encodes = repository.list_encodes_by_uuid(db, query.media_uuid)

    return encodes


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
