from fastapi import HTTPException, APIRouter
import requests
from .config import (
    RABBITMQ_MANAGEMENT_URL,
)

router = APIRouter()


@router.get("/healthcheck/api", include_in_schema=False)
def healthcheck():
    return {"status": "OK"}


@router.get("/healthcheck/rabbitmq")
def rabbitmq_healthcheck():
    try:
        response = requests.get(RABBITMQ_MANAGEMENT_URL)
        data = response.json()

        if response.status_code != 200 or data["status"] != "ok":
            raise HTTPException(status_code=500, detail="RabbitMQ is not healthy")

        return {"status": "OK"}

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to connect to RabbitMQ: {e}"
        )
