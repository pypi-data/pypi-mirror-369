from av.stream import Stream
from av import open as av_open


class VideoWriter:
    """
    Class to write video files with the PyAv (av)
    library that uses ffmpeg on the background.
    """

    def __init__(
        self,
        filename: str,
        fps: float,
        size: tuple[int, int],
        pixel_format: str = 'yuv420p'
    ):
        self.filename: str = filename
        """
        The filename we want to use to save the video
        file.
        """
        # TODO: What about this 'libx264' (?)
        self._output = av_open(filename, mode = 'w')
        self._stream: Stream = self._output.add_stream("libx264", rate = fps)
        self._stream.width = size[0]
        self._stream.height = size[1]
        self._stream.pix_fmt = pixel_format