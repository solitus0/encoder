import threading
from fastapi import FastAPI, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from encoder import file_system, models
from encoder.database import engine, get_db
from .media_encoder import EncodeCompletionHandler
from encoder.rabbitmq import RabbitMQConsumer
from pydantic.error_wrappers import ValidationError
from encoder.config import RABBITMQ_RESULTS_QUEUE
from starlette.responses import StreamingResponse
from encoder.api import router
from fastapi.responses import JSONResponse
import logging
from encoder.logging import configure_logging

log = logging.getLogger(__name__)
configure_logging()

models.Base.metadata.create_all(bind=engine)
api = FastAPI()

# Add CORS middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


try:
    consumer = RabbitMQConsumer(RABBITMQ_RESULTS_QUEUE)
except Exception:
    raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ")


@api.on_event("startup")
async def startup_event():
    db = next(get_db())
    fileManager = file_system.FileManager(db)
    encoder = EncodeCompletionHandler(db, fileManager)
    consumer_thread = threading.Thread(
        target=consumer.start, args=(encoder.on_message_receive,)
    )
    consumer_thread.start()


@api.on_event("shutdown")
async def shutdown_event():
    consumer.stop()


api.include_router(router)


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


api.add_middleware(ExceptionMiddleware)
