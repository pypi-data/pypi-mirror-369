from av.stream import Stream
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.container.output import OutputContainer
from av import open as av_open
from fractions import Fraction
from typing import Union


class VideoWriter:
    """
    Class to write video files with the PyAv (av)
    library that uses ffmpeg on the background.
    """

    def __init__(
        self,
        filename: str,
    ):
        self.filename: str = filename
        """
        The filename we want to use to save the video
        file.
        """
        # TODO: What about this 'libx264' (?)
        self.output: OutputContainer = av_open(filename, mode = 'w')
        """
        An OutputContainer to control the writing process.
        """
        self.video_stream: VideoStream = None
        """
        The video stream.
        """
        self.audio_stream: AudioStream = None
        """
        The audio stream.
        """

    def set_video_stream(
        self,
        codec_name: Union[str, None],
        fps: Union[Fraction, int, float, None],
        size: Union[tuple[int, int], None] = None,
        pixel_format: Union[str, None] = None,
        options: Union[dict[str, str], None] = None
    ) -> 'VideoWriter':
        """
        Set the video stream, that will overwrite any other
        previous video stream set.
        """
        self.video_stream: VideoStream = self.output.add_stream(
            # TODO: Maybe 'libx264' as default 'codec_name' (?)
            codec_name = codec_name,
            rate = fps,
            options = options
        )

        if size is not None:
            self.video_stream.width = size[0]
            self.video_stream.height = size[1]

        if pixel_format is not None:
            # TODO: Maybe 'yuv420p' as default 'pixel_format' (?)
            self.video_stream.pix_fmt = pixel_format

        return self

    # TODO: Maybe 'add_video_stream_from_template' (?)

    def set_audio_stream(
        self,
        codec_name: Union[str, None]
        # TODO: Add more if needed
    ) -> 'VideoWriter':
        """
        Set the audio stream, that will overwrite any other
        previous audio stream set.
        """
        self.audio_stream: AudioStream = self.output.add_stream(
            codec_name = codec_name
        )

        # TODO: Add more if needed

        return self

    def set_audio_stream_from_template(
        self,
        template: Stream
    ) -> 'VideoWriter':
        """
        Set the audio stream, that will overwrite any other
        previous audio stream set.

        You can pass the audio stream as it was
        obtained from the reader.
        """
        self.audio_stream: AudioStream = self.output.add_stream_from_template(
            template
        )

        return self

"""
# TODO: Check 'https://www.youtube.com/watch?v=OlNWCpFdVMA'
# for ffmpeg with mp3 access
"""