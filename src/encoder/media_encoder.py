import json

import ffmpeg
from sqlalchemy.orm import Session

from . import crud, file_system, models, rabbitmq, schemas


class MediaEncoder:
    def __init__(self, db: Session, file_manager: file_system.FileManager):
        self.db = db
        self.file_manager = file_manager

    def encode(self, media: models.Media, preset: schemas.Preset) -> models.Encode:
        if not self.file_manager.file_exist(media.file_path):
            return None

        command = self._construct_ffmpeg_command(media, preset)
        message = self._prepare_encode_data(media, command)

        self._push_to_queue(message)

    def batch_encode(
        self, media_list: list[models.Media], preset: schemas.Preset
    ) -> list[models.Encode]:
        for media in media_list:
            self.encode(media, preset)

    def _construct_ffmpeg_command(self, media: models.Media, preset: schemas.Preset):
        original_path = media.file_path
        temp_path = self.file_manager.get_encode_temp_path(original_path)

        return ffmpeg.input(original_path).output(
            temp_path,
            format=preset.FileFormat,
            acodec=preset.AudioEncoder,
            ab=preset.AudioBitrate,
            ac=preset.AudioMixdown,
            ar=preset.AudioSamplerate,
            vcodec=preset.VideoEncoder,
            vf=f"scale={preset.PictureWidth}:{preset.PictureHeight}",
            preset=preset.VideoPreset,
            crf=preset.VideoQualitySlider,
            y=None,
            metadata=f"media_uuid={media.uuid}",
        )

    def _prepare_encode_data(self, media: models.Media, command) -> schemas.QueueEncode:
        data = schemas.InitializeEncode(
            media_uuid=media.uuid,
            status=schemas.EncodeStatusEnum.queued,
            source_path=media.file_path,
            temp_path=self.file_manager.get_encode_temp_path(media.file_path),
            source_size=self.file_manager.get_file_size_mb(media.file_path),
            command=command.get_args(),
        )

        encode = crud.initialize_encode(self.db, data)
        queue_data = schemas.QueueEncode.from_orm(encode)
        queue_data.duration_in_seconds = media.duration

        return queue_data

    def _push_to_queue(self, message: schemas.QueueEncode):
        rabbitmq_client = rabbitmq.RabbitMQProducer()
        rabbitmq_client.push_message(message.model_dump_json())


class EncodeCompletionHandler:
    def __init__(self, db: Session, file_manager: file_system.FileManager):
        self.db = db
        self.file_manager = file_manager

    def on_message_receive(self, channel, method, properties, body):
        print(f"Received message {body}")
        finishEncode = schemas.EncodeComplete(**json.loads(body))

        encode = crud.get_encode_by_uuid(self.db, finishEncode.id)
        encode.status = schemas.EncodeStatusEnum.finished
        encode.output_size = self.file_manager.get_file_size_mb(encode.temp_path)

        encode.duration_in_seconds = finishEncode.duration

        if self.file_manager.file_exist(encode.source_path):
            self.file_manager.move_original_to_temp(encode.source_path)
            self.file_manager.move_file(encode.temp_path, encode.source_path)

        self.db.commit()

        channel.basic_ack(delivery_tag=method.delivery_tag)
