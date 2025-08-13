"""
A video reader using the PyAv (av) library
that, using ffmpeg, detects the video.
"""
from fractions import Fraction

import av


class VideoReader:
    """
    Class to read video files with the PyAv (av)
    library that uses ffmpeg on the background.
    """

    @property
    def frame_iterator(
        self
    ):
        """
        Iterator to iterate over all the video frames
        decodified.
        """
        return self._container.decode(self._video_stream)
    
    @property
    def next_frame(
        self
    ):
        """
        Get the next frame of the iterator.
        """
        return next(self.frame_iterator)
    
    @property
    def fps(
        self
    ) -> Fraction:
        """
        The fps of the video.
        """
        # They return it as a Fraction but...
        return self._video_stream.average_rate
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the video in a (width, height) format.
        """
        return (
            self._video_stream.width,
            self._video_stream.height
        )
    
    @property
    def width(
        self
    ) -> int:
        """
        The width of the video, in pixels.
        """
        return self.size[0]
    
    @property
    def height(
        self
    ) -> int:
        """
        The height of the video, in pixels.
        """
        return self.size[1]
    
    # Any property related to audio has to
    # start with 'audio_property_name'

    def __init__(
        self,
        filename: str
    ):
        self.filename: str = filename
        """
        The filename of the video source.
        """
        self._container: av.InputContainer = av.open(filename)
        """
        The av input general container of the
        video (that also includes the audio) we
        are reading.
        """
        self._video_stream = self._container.streams.video[0]
        """
        The stream that includes the video.
        """
        self._video_stream.thread_type = "AUTO"
        self._audio_stream = self._container.streams.audio[0]
        """
        The stream that includes the audio.
        """
        self._audio_stream.thread_type = "AUTO"




"""
Read this below if you can to combine videos
that have not been written yet to the disk
(maybe a composition in moviepy or I don't
know).

Usar un pipe (sin escribir archivo completo)
Puedes lanzar un proceso FFmpeg que envíe el vídeo a PyAV por stdin como flujo sin codificar (por ejemplo en rawvideo), así no tienes que escribir el archivo final.
Ejemplo:

PYTHON_CODE:
import subprocess
import av

# FFmpeg produce frames en crudo por stdout
ffmpeg_proc = subprocess.Popen(
    [
        "ffmpeg",
        "-i", "-",       # Lee de stdin
        "-f", "rawvideo",
        "-pix_fmt", "rgba",
        "-"
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE
)

# Aquí enviarías los datos combinados desde tu programa al ffmpeg_proc.stdin
# y podrías leer con PyAV o directamente procesar arrays de píxeles

Esto es lo más usado para pipeline de vídeo en tiempo real.
"""