import logging

from sqlalchemy.orm import Session

from . import crud
from .ffmpeg import FfmpegWrapper
from .file_system import DirectoryScanner


class MediaScanner:
    def __init__(self, db: Session):
        self.db = db
        self.scanner = DirectoryScanner(db)

    def process_file(self, file):
        try:
            ffmpeg = FfmpegWrapper(file)
            data = ffmpeg.data
            media = crud.get_by_uuid(self.db, data.uuid) or crud.get_by_file_path(
                self.db, data.file_path
            )

            if media:
                if crud.should_update(data, media):
                    crud.update_media(self.db, media, data)
            else:
                logging.info(f"Creating new media: {data.file_path}")
                crud.create_media(self.db, data)

            return data.file_path
        except Exception as e:
            logging.error(f"Error processing {file}: {e}")
            return None

    def delete_unprocessed_media(self, successfully_processed_paths):
        for media in crud.all(self.db):
            if media.file_path not in successfully_processed_paths:
                logging.info(f"Deleting media entity {media.file_path}")
                self.db.delete(media)
                self.db.commit()

    def scan(self):
        files = self.scanner.scan_for_media_files()

        successfully_processed_paths = set()

        for file in files:
            processed_path = self.process_file(file)
            if processed_path:
                successfully_processed_paths.add(processed_path)

        self.delete_unprocessed_media(successfully_processed_paths)

        return list(successfully_processed_paths)
