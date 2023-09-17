import ffmpeg
from sqlalchemy.orm import Session

from encoder.media import file_system

from encoder import rabbitmq
from encoder.encode import repository, schemas
from encoder.config import RABBITMQ_ENCODE_QUEUE
from encoder.media.entity import Media
from encoder.encode.entity import Encode
from encoder.encode.schemas import QueueEncode
from encoder.preset.schemas import Preset


class EncodeEnqueuer:
    def __init__(self, db: Session, file_manager: file_system.FileManager):
        self.db = db
        self.file_manager = file_manager

    def enqueue_media_for_processing(self, media: Media, preset: Preset) -> Encode:
        if not self.file_manager.file_exist(media.file_path):
            return None

        command = self._build_ffmpeg_command(media, preset)
        message = self._prepare_encode_data(media, command)

        self._enqueue_message(message)

    def enqueue_for_processing(
        self, media_list: list[Media], preset: Preset
    ) -> list[Encode]:
        for media in media_list:
            self.enqueue_media_for_processing(media, preset)

    def _build_ffmpeg_command(self, media: Media, preset: Preset):
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

    def _prepare_encode_data(self, media: Media, command) -> QueueEncode:
        data = schemas.InitializeEncode(
            media_uuid=media.uuid,
            status=schemas.EncodeStatusEnum.queued,
            source_path=media.file_path,
            temp_path=self.file_manager.get_encode_temp_path(media.file_path),
            source_size=self.file_manager.get_file_size_mb(media.file_path),
            command=command.get_args(),
        )

        encode = repository.initialize_encode(self.db, data)
        queue_data = QueueEncode.from_orm(encode)
        queue_data.duration_in_seconds = media.duration

        return queue_data

    def _enqueue_message(self, message: QueueEncode):
        rabbitmq_client = rabbitmq.RabbitMQProducer()
        rabbitmq_client.push_message(RABBITMQ_ENCODE_QUEUE, message.model_dump_json())
