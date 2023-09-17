import logging
from sqlalchemy.orm import Session
from encoder.media import schemas
from encoder.media.file_system import DirectoryScanner
from encoder.rabbitmq import RabbitMQProducer
from encoder.config import RABBITMQ_PROBE_QUEUE
from encoder.media import repository


class MediaEnqueuer:
    def __init__(self, db: Session):
        self.db = db
        self.scanner = DirectoryScanner(db)
        self.rabbitmq_client = RabbitMQProducer()

    def process_all_media_files(self):
        media_files = self.scanner.scan_for_media_files()

        for media_file in media_files:
            self.enqueue_file_for_processing(media_file)

        self.rabbitmq_client.close()
        self.remove_unprocessed_media_entries(media_files)

    def enqueue_file_for_processing(self, media_file):
        try:
            message = schemas.QueueScan(source_path=media_file)
            self._enqueue_message(message)
        except Exception as e:
            logging.error(f"Error enqueuing {media_file}: {e}")

    def _enqueue_message(self, message: schemas.QueueScan):
        self.rabbitmq_client.push_message(
            RABBITMQ_PROBE_QUEUE, message.model_dump_json()
        )

    def remove_unprocessed_media_entries(self, files):
        for media in repository.all(self.db):
            if media.file_path not in files:
                logging.info(f"Removing media entry {media.file_path}")
                self.db.delete(media)
                self.db.commit()
