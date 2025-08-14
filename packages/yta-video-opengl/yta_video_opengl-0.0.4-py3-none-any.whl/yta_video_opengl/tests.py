"""
Manual tests that are working and are interesting
to learn about the code, refactor and build
classes.
"""
from yta_validation import PythonValidator
from yta_video_opengl.reader import VideoReader
from yta_video_opengl.writer import VideoWriter
from yta_timer import Timer
from yta_video_frame_time import T

import av
import moderngl
import numpy as np


def video_modified_stored():
    VIDEO_PATH = "test_files/test_1.mp4"
    OUTPUT_PATH = "test_files/output.mp4"
    AMP = 0.05
    FREQ = 10.0
    SPEED = 2.0

    # ModernGL context without window
    context = moderngl.create_standalone_context()

    # Wave shader vertex and fragment
    program = context.program(
        vertex_shader = '''
        #version 330
        in vec2 in_pos;
        in vec2 in_uv;
        out vec2 v_uv;
        void main() {
            v_uv = in_uv;
            gl_Position = vec4(in_pos, 0.0, 1.0);
        }
        ''',
        fragment_shader = '''
        #version 330
        uniform sampler2D tex;
        uniform float time;
        uniform float amp;
        uniform float freq;
        uniform float speed;
        in vec2 v_uv;
        out vec4 f_color;
        void main() {
            float wave = sin(v_uv.x * freq + time * speed) * amp;
            vec2 uv = vec2(v_uv.x, v_uv.y + wave);
            f_color = texture(tex, uv);
        }
        '''
    )

    # Quad
    vertices = np.array([
        -1, -1, 0.0, 0.0,
        1, -1, 1.0, 0.0,
        -1,  1, 0.0, 1.0,
        1,  1, 1.0, 1.0,
    ], dtype = 'f4')
    vbo = context.buffer(vertices.tobytes())
    vao = context.simple_vertex_array(program, vbo, 'in_pos', 'in_uv')

    video = VideoReader(VIDEO_PATH)

    print(video.number_of_frames)
    print(video.number_of_audio_frames)

    # TODO: This has to be dynamic, but
    # according to what (?)
    NUMPY_FORMAT = 'rgb24'
    # TODO: Where do we obtain this from (?)
    VIDEO_CODEC_NAME = 'libx264'
    # TODO: Where do we obtain this from (?)
    PIXEL_FORMAT = 'yuv420p'

    # Framebuffer to render
    fbo = context.simple_framebuffer(video.size)
    fbo.use()

    # Decode first frame and use as texture
    first_frame = video.next_frame

    # Most of OpenGL textures expect origin in lower
    # left corner
    # TODO: What if alpha (?)
    image = np.flipud(first_frame.to_ndarray(format = NUMPY_FORMAT))
    texture = context.texture((image.shape[1], image.shape[0]), 3, image.tobytes())

    texture.build_mipmaps()

    # Uniforms
    program['amp'].value = AMP
    program['freq'].value = FREQ
    program['speed'].value = SPEED

    # Writer with H.264 codec
    video_writer = (
        VideoWriter(OUTPUT_PATH)
        .set_video_stream(VIDEO_CODEC_NAME, video.fps, video.size, PIXEL_FORMAT)
        .set_audio_stream_from_template(video.audio_stream)
    )

    frame_index = 0
    for frame_or_packet in video.iterate_with_audio(
        do_decode_video = True,
        do_decode_audio = False
    ):
        # This below is because of the parameters we
        # passed to the method
        is_video_frame = PythonValidator.is_instance_of(frame_or_packet, 'VideoReaderFrame')
        is_audio_packet = PythonValidator.is_instance_of(frame_or_packet, 'VideoReaderPacket')

        # To simplify the process
        if frame_or_packet is not None:
            frame_or_packet = frame_or_packet.data

        if is_audio_packet:
            video_writer.mux(frame_or_packet)
        elif is_video_frame:
            with Timer(is_silent_as_context = True) as timer:

                def process_frame(
                    frame: 'VideoFrame'
                ):
                    # Add some variables if we need, for the
                    # opengl change we are applying (check the
                    # program code)
                    program['time'].value = T.video_frame_index_to_video_frame_time(frame_index, float(video.fps))
                    
                    # To numpy RGB inverted for OpenGL
                    img_array = np.flipud(
                        frame.to_ndarray(format = NUMPY_FORMAT)
                    )

                    # Create texture
                    texture = context.texture((img_array.shape[1], img_array.shape[0]), 3, img_array.tobytes())
                    texture.use()

                    # Render with shader to frame buffer
                    fbo.use()
                    vao.render(moderngl.TRIANGLE_STRIP)

                    # Processed GPU result to numpy
                    processed_data = np.frombuffer(
                        fbo.read(components = 3, alignment = 1), dtype = np.uint8
                    )
                    # Invert numpy to normal frame
                    processed_data = np.flipud(
                        processed_data.reshape((img_array.shape[0], img_array.shape[1], 3))
                    )

                    # To VideoFrame and to buffer
                    frame = av.VideoFrame.from_ndarray(processed_data, format = NUMPY_FORMAT)
                    # TODO: What is this for (?)
                    #out_frame.pict_type = 'NONE'
                    return frame

                video_writer.mux_video_frame(process_frame(frame_or_packet))

            print(f'Frame {str(frame_index)}: {timer.time_elapsed_str}s')
            frame_index += 1

    # While this code can be finished, the work in
    # the muxer could be not finished and have some
    # packets waiting to be written. Here we tell
    # the muxer to process all those packets.
    video_writer.mux_video_frame(None)

    # TODO: Maybe move this to the '__del__' (?)
    video_writer.output.close()
    video.container.close()
    print(f'Saved as "{OUTPUT_PATH}".')