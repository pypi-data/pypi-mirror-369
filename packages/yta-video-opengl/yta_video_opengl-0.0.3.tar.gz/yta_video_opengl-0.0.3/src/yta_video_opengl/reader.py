"""
A video reader using the PyAv (av) library
that, using ffmpeg, detects the video.
"""
from yta_validation import PythonValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from av.packet import Packet
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.container.input import InputContainer
from fractions import Fraction
from av import open as av_open
from typing import Union


class VideoReaderFrame:
    """
    Class to wrap a frame of a video that is
    being read, that can be a video or audio
    frame.
    """

    @property
    def is_packet(
        self
    ) -> bool:
        """
        Flag to indicate if the frame is actually
        a packet of frames.
        """
        return PythonValidator.is_instance_of(self.frame, Packet)

    @property
    def is_video_frame(
        self
    ):
        """
        Flag to indicate if the instance is a video
        frame.
        """
        return PythonValidator.is_instance_of(self.frame, VideoFrame)
    
    @property
    def is_audio_frame(
        self
    ):
        """
        Flag to indicate if the instance is an audio
        frame.
        """
        return PythonValidator.is_instance_of(self.frame, AudioFrame)
    
    @property
    def is_video_packet(
        self
    ) -> bool:
        """
        Flag to indicate if the instance is a packet
        containing video frames.
        """
        return (
            self.is_packet and
            self.frame.stream.type == 'video'
        )

    @property
    def is_audio_packet(
        self
    ) -> bool:
        """
        Flag to indicate if the instance is a packet
        containing audio frames.
        """
        return (
            self.is_packet and
            self.frame.stream.type == 'audio'
        )
    
    def __init__(
        self,
        # TODO: Add the type, please
        frame: any
    ):
        self.frame: Union[AudioFrame, VideoFrame, Packet] = frame
        """
        The frame content, that can be audio or video
        frame, or a packet of more than one frame.
        """

    def test():
        # If packet we need to do this (if we want)
        # to decode
        #for frame in packet.decode():
        
        # In the output we need to 'mux' packets,
        # always
        pass

    # The '.decode()' generates a list of Packet
    # The '.encode()' receives a list of Packet
    # The '.demux()' extract packets from a single input
    # The '.mux()' mix packets into a single output
        

class VideoReader:
    """
    Class to read video files with the PyAv (av)
    library that uses ffmpeg on the background.
    """

    @property
    def frame_iterator(
        self
    ) -> 'Iterator[VideoFrame]':
        """
        Iterator to iterate over all the video frames
        decodified.
        """
        return self.container.decode(self.video_stream)
    
    @property
    def next_frame(
        self
    ) -> Union[VideoFrame, None]:
        """
        Get the next frame of the iterator.
        """
        return next(self.frame_iterator)
    
    # TODO: Maybe rename (?)
    @property
    def frame_with_audio_iterator(
        self
    ) -> 'Iterator[Packet]':
        """
        Iterator to iterate over all the video frames
        decodified, including also the audio.
        """
        return self.container.demux((self.video_stream, self.audio_stream))

    @property
    def next_frame_with_audio(
        self
    ) -> Union[Packet, None]:
        """
        Get the next frame of the iterator that includes
        the audio.
        """
        return next(self.frame_with_audio_iterator)

    @property
    def codec_name(
        self
    ) -> str:
        """
        Get the name of the video codec.
        """
        return self.video_stream.codec_context.name
    
    @property
    def audio_codec_name(
        self
    ) -> str:
        """
        Get the name of the audio codec.
        """
        return self.audio_stream.codec_context.name
    
    @property
    def fps(
        self
    ) -> Fraction:
        """
        The fps of the video.
        """
        # They return it as a Fraction but...
        return self.video_stream.average_rate
    
    @property
    def audio_fps(
        self
    ) -> Fraction:
        """
        The fps of the audio.
        """
        # TODO: What if no audio (?)
        return self.audio_stream.average_rate
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the video in a (width, height) format.
        """
        return (
            self.video_stream.width,
            self.video_stream.height
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
        self.container: InputContainer = av_open(filename)
        """
        The av input general container of the
        video (that also includes the audio) we
        are reading.
        """
        self.video_stream: VideoStream = self.container.streams.video[0]
        """
        The stream that includes the video.
        """
        self.video_stream.thread_type = 'AUTO'
        # TODO: What if no audio (?)
        self.audio_stream: AudioStream = self.container.streams.audio[0]
        """
        The stream that includes the audio.
        """
        self.audio_stream.thread_type = 'AUTO'

    def iterate(
        self
    ):
        for frame in self.frame_iterator:
            yield VideoReaderFrame(frame)

    def iterate_with_audio(
        self
    ):
        for frame_or_packet in self.frame_with_audio_iterator:
            yield VideoReaderFrame(frame_or_packet)




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