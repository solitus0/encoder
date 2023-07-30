from sqlalchemy.orm import Session

from . import crud
from .ffmpeg import FfmpegWrapper
from .file_system import FileSystem


class MediaScanner:
    def __init__(self, db: Session, root_path: str, scan_folder: str):
        self.db = db
        self.file_system = FileSystem(root_path, scan_folder)

    def scan(self):
        files = self.file_system.scan_dir_files()

        results = []
        for file in files:
            data = FfmpegWrapper(file).data

            results.append(data)

        for data in results:
            media_db = crud.get_by_file_path(self.db, data.file_path)
            if media_db:
                should_update = crud.should_update(data, media_db)
                if should_update:
                    crud.update_media(self.db, media_db, data)
            else:
                crud.create_media(self.db, data)

        media_paths = [file.file_path for file in results]
        for media_db in crud.get_medias(self.db):
            if media_db.file_path not in media_paths:
                self.db.delete(media_db)
                self.db.commit()

        return results
