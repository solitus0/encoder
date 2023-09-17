import os
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from encoder.media import repository, schemas
from encoder.database import get_db
from encoder.media.enqueuer import MediaEnqueuer
from encoder.permissions.security import decorate_media_with_permissions


router = APIRouter()


@router.post("/api/scan", tags=["media"], status_code=204)
def scan(
    db: Session = Depends(get_db),
):
    scanner = MediaEnqueuer(db)
    scanner.process_all_media_files()


@router.get(
    "/api/media",
    response_model=schemas.PaginationResponse,
    tags=["media"],
)
def list_media(
    filter: schemas.PaginationFilter = Depends(),
    db: Session = Depends(get_db),
) -> schemas.PaginationResponse:
    media = repository.get_by_filter(db, filter)

    for item in media.items:
        decorate_media_with_permissions(item)

    return media


@router.post("/api/directory/validate", tags=["directory"], status_code=204)
def validate(
    command: schemas.ScanCommand,
):
    directory = command.scan_path
    if os.path.isdir(directory):
        return
    else:
        raise HTTPException(status_code=400, detail="Invalid directory path")
