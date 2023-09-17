from fastapi import APIRouter
from encoder.preset import presets

from encoder.preset import schemas

router = APIRouter()


@router.get("/api/presets", response_model=list[schemas.Preset], tags=["media"])
def list_presets():
    collection = presets.PresetsCollection()
    presets_list = collection.all()

    return presets_list
