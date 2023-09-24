import os
from typing import Optional
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from encoder.setting import schemas
from encoder.database import get_db
from encoder.setting import repository
import requests
from encoder.config import (
    RABBITMQ_MANAGEMENT_URL,
)

router = APIRouter()


@router.get("/api/permissions", tags=["permissions"])
def get_permissions(db: Session = Depends(get_db)):
    def check_path(path: Optional[schemas.SettingsBase]) -> bool:
        if not path:
            return False
        return os.path.isdir(path.value) and os.access(path.value, os.W_OK)

    scan_dir_settings = repository.get_by_key(db, schemas.SettingKeyEnum.scan_path)
    temp_path = repository.get_setting(db, schemas.SettingKeyEnum.temp_path)
    rabbitmq_health = rabbitmq_health_check()

    is_temp_path_ok = check_path(temp_path)

    is_scan_path_ok = False
    for scan_path in scan_dir_settings:
        is_scan_path_ok = check_path(scan_path)
        if is_scan_path_ok:
            break

    return {
        "scan_path": is_scan_path_ok,
        "temp_path": is_temp_path_ok,
        "rabbitmq": rabbitmq_health,
        "scan": is_scan_path_ok and rabbitmq_health,
        "encode": is_temp_path_ok and rabbitmq_health,
    }


def rabbitmq_health_check() -> bool:
    try:
        response = requests.get(RABBITMQ_MANAGEMENT_URL)
        data = response.json()

        if response.status_code != 200 or data["status"] != "ok":
            return False

        return True

    except requests.RequestException:
        return False
