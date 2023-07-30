import os
import subprocess

from . import schemas


class FfmpegWrapper:
    def __init__(self, source_path: str):
        self._source_path = source_path
        self._streams_data = self.stream_info(source_path)
        self._video_streams = self.get_stream("video")
        self._audio_streams = self.get_stream("audio")
        self._subtitle_streams = self.get_stream("subtitle")
        self._attachment_streams = self.get_stream("attachment")

    @property
    def source_path(self) -> str:
        return self._source_path

    @property
    def streams_data(self) -> list:
        return self._streams_data

    @property
    def video_streams(self) -> list:
        return self._video_streams

    @property
    def audio_streams(self) -> list:
        return self._audio_streams

    @property
    def subtitle_streams(self) -> list:
        return self._subtitle_streams

    @property
    def attachment_streams(self) -> list:
        return self._attachment_streams

    def stream_info(self, source_path: str) -> list:
        is_file = os.path.isfile(source_path)
        if not is_file:
            raise Exception(
                f"Failed to get streams data. File not found: {source_path}"
            )

        ffprobe_output = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", source_path],
            stdout=subprocess.PIPE,
        ).stdout.decode()

        stream_lines = ffprobe_output.strip().split("\n")
        streams = []
        current_stream = -1
        for line in stream_lines:
            if line == "[STREAM]":
                current_stream += 1
                streams.append([])
            elif line == "[/STREAM]":
                continue
            else:
                streams[current_stream].append(line)

        formated_streams = []
        for index, stream in enumerate(streams):
            formated_streams.append({})
            for line in stream:
                key, value = line.split("=")
                formated_streams[index][key] = value

        return formated_streams

    def get_stream(self, type: str) -> list:
        streams = self.streams_data

        return [stream for stream in streams if stream["codec_type"] == type]

    def get_file_size(self, file_path):
        if not os.path.exists(file_path):
            return None

        size = os.path.getsize(file_path)
        mb = f"{size / 1024 / 1024:.2f}"

        return float(mb)

    @property
    def data(self) -> schemas.MediaCreate:
        video_codec = [stream["codec_name"] for stream in self.video_streams]
        audio_codec = [stream["codec_name"] for stream in self.audio_streams]
        subs_codec = [stream["codec_name"] for stream in self.subtitle_streams]
        width = int(self.video_streams[0]["width"])
        height = int(self.video_streams[0]["height"])
        file_size = self.get_file_size(self.source_path)

        media = schemas.MediaCreate(
            file_path=self.source_path,
            file_size=file_size,
            video_codec=video_codec,
            audio_codec=audio_codec,
            subtitle_codec=subs_codec,
            width=width,
            height=height,
        )

        return media
