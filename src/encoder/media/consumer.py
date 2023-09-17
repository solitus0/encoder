import logging
from sqlalchemy.orm import Session
from encoder.media import repository, schemas


class MediaDataQueueConsumer:
    def __init__(self, db: Session):
        self.db = db

    def on_message_receive(self, channel, method, properties, body):
        logging.info(f"Received message: {body}")

        try:
            data = schemas.MediaCreate.model_validate_json(body)
            media = repository.get_by_uuid(
                self.db, data.uuid
            ) or repository.get_by_file_path(self.db, data.file_path)

            if media:
                if repository.should_update(data, media):
                    repository.update_media(self.db, media, data)
            else:
                logging.info(f"Creating new media: {data.file_path}")
                repository.create_media(self.db, data)
        except Exception as e:
            logging.error(f"Error processing message: {e}")

        channel.basic_ack(delivery_tag=method.delivery_tag)
