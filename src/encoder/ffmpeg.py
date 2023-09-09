import hashlib
import os
import uuid

import ffmpeg

from . import schemas


class FfmpegWrapper:
    def __init__(self, source_path: str):
        self._source_path = source_path

    def get_file_size(self, file_path):
        if not os.path.exists(file_path):
            return None

        size = os.path.getsize(file_path)
        mb = f"{size / 1024 / 1024:.2f}"

        return float(mb)

    def sha256_encode(self, data: str) -> str:
        byte_data = data.encode("utf-8")
        hashed = hashlib.sha256(byte_data)

        return hashed.hexdigest()

    @property
    def data(self) -> schemas.MediaCreate:
        info = ffmpeg.probe(self._source_path)
        data = schemas.MediaMetadata(**info)

        video_streams = data.get_streams("video")
        audio_streams = data.get_streams("audio")
        subs_streams = data.get_streams("subtitle")

        has_video = len(video_streams) > 0
        has_audio = len(audio_streams) > 0
        has_subs = len(subs_streams) > 0
        if not has_video:
            raise Exception("No video stream found")
        
        if not has_audio:
            raise Exception("No audio stream found")
        
        if not has_subs:
            print("No subtitle stream found")

        video_codec = [stream.codec_name for stream in video_streams]
        audio_codec = [stream.codec_name for stream in audio_streams]
        subs_codec = [stream.codec_name for stream in subs_streams]

        width = int(video_streams[0].width)
        height = int(video_streams[0].height)
        dimesions = f"{width}x{height}"
        file_size = self.get_file_size(self._source_path)
        file_name = os.path.splitext(os.path.basename(self._source_path))[0]
        duration = float(data.format.duration) if data.format.duration else None

        uuid_string = data.get_tag("MEDIA_UUID")
        if not uuid_string:
            uuid_string = str(uuid.uuid4())

        media = schemas.MediaCreate(
            uuid=uuid_string,
            file_path=self._source_path,
            file_name=file_name,
            dimensions=dimesions,
            file_size=file_size,
            video_codec=video_codec,
            audio_codec=audio_codec,
            subtitle_codec=subs_codec,
            duration=duration,
        )

        return media
