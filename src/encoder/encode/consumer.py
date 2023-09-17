import json
from sqlalchemy.orm import Session

from encoder.media import file_system

from encoder.encode import schemas, repository


class MediaEncodeQueueConsumer:
    def __init__(self, db: Session, file_manager: file_system.FileManager):
        self.db = db
        self.file_manager = file_manager

    def on_message_receive(self, channel, method, properties, body):
        print(f"Received message {body}")
        finishEncode = schemas.EncodeComplete(**json.loads(body))

        encode = repository.get_encode_by_uuid(self.db, finishEncode.id)
        if not encode:
            print(f"Encoding not found: {finishEncode.id}")
            channel.basic_ack(delivery_tag=method.delivery_tag)

        encode.status = schemas.EncodeStatusEnum.finished
        encode.output_size = self.file_manager.get_file_size_mb(encode.temp_path)
        encode.duration_in_seconds = finishEncode.duration

        if self.file_manager.file_exist(encode.source_path):
            self.file_manager.move_original_to_temp(encode.source_path)
            self.file_manager.move_file(encode.temp_path, encode.source_path)

        self.db.commit()

        channel.basic_ack(delivery_tag=method.delivery_tag)
