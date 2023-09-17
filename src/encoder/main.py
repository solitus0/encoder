from fastapi import FastAPI, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from encoder.setting import entity
from encoder.database import engine, get_db
from encoder.media import file_system
from encoder.encode.consumer import MediaEncodeQueueConsumer
from encoder.rabbitmq import RabbitMQConsumer
from pydantic import ValidationError
from encoder.config import RABBITMQ_ENCODE_RESULTS_QUEUE, RABBITMQ_PROBE_RESULT_QUEUE
from starlette.responses import StreamingResponse
from encoder.encode.api import router as encoder_api
from encoder.media.api import router as media_api
from encoder.setting.api import router as setting_api
from encoder.preset.api import router as preset_api
from encoder.permissions.api import router as permission_api
from encoder.api import router as main_api
from encoder.media.consumer import MediaDataQueueConsumer
from fastapi.responses import JSONResponse
import logging
from encoder.logging import configure_logging
import threading

log = logging.getLogger(__name__)
configure_logging()

entity.Base.metadata.create_all(bind=engine)
api = FastAPI()
consumers = []


@api.on_event("startup")
async def startup_event():
    try:
        db = next(get_db())
        fileManager = file_system.FileManager(db)

        # Media Encode Consumer
        media_consumer = MediaEncodeQueueConsumer(db, fileManager)
        encode_connection = RabbitMQConsumer()
        encode_connection.start(
            RABBITMQ_ENCODE_RESULTS_QUEUE, media_consumer.on_message_receive
        )
        consumers.append(encode_connection)

        # Scan Consumer
        scan_consumer = MediaDataQueueConsumer(db)
        scan_connection = RabbitMQConsumer()
        scan_connection.start(
            RABBITMQ_PROBE_RESULT_QUEUE, scan_consumer.on_message_receive
        )

        consumers.append(scan_connection)

    except Exception as e:
        logging.error(f"Failed to connect to RabbitMQ: {e}")


@api.on_event("shutdown")
async def shutdown_event():
    all_threads = threading.enumerate()

    for consumer in consumers:
        consumer.stop()

    for thread in all_threads:
        if thread is not threading.current_thread():
            thread.join(timeout=2)


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> StreamingResponse:
        try:
            response = await call_next(request)
        except ValidationError as e:
            log.exception(e)
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": e.errors()},
            )
        except ValueError as e:
            log.exception(e)
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "detail": [
                        {"msg": "Unknown", "loc": ["Unknown"], "type": "Unknown"}
                    ]
                },
            )
        except Exception as e:
            log.exception(e)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": [
                        {"msg": "Unknown", "loc": ["Unknown"], "type": "Unknown"}
                    ]
                },
            )

        return response


api.include_router(media_api)
api.include_router(encoder_api)
api.include_router(setting_api)
api.include_router(preset_api)
api.include_router(permission_api)
api.include_router(main_api)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

api.add_middleware(ExceptionMiddleware)
