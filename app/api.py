from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from .scanner import MediaScanner

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/media", response_model=list[schemas.Media], tags=["media"])
def list_media(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_medias(db, skip=offset, limit=limit)

    return users


@app.post("/api/scan", response_model=list[schemas.MediaCreate], tags=["media"])
def scan(db: Session = Depends(get_db)):
    scanner = MediaScanner(db, "/Users/ernestas/Downloads/media", "Anime Series FHD")
    media = scanner.scan()

    return media
