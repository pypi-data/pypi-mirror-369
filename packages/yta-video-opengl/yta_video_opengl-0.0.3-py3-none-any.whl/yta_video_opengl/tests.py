"""
Manual tests that are working and are interesting
to learn about the code, refactor and build
classes.
"""
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
    # for frame in video.frame_iterator:
    #     with Timer(is_silent_as_context = True) as timer:
    #         program['time'].value = T.video_frame_index_to_video_frame_time(frame_index, float(video.fps))

    #         # To numpy array and flip to OpenGL coordinates
    #         image_array = np.flipud(
    #             frame.to_ndarray(format = 'rgb24')
    #         )

    #         # Create texture
    #         texture = context.texture((image_array.shape[1], image_array.shape[0]), 3, image_array.tobytes())
    #         # Add frame to texture
    #         image = frame.to_image().transpose(Image.FLIP_TOP_BOTTOM).convert('RGB')
    #         texture.write(image.tobytes())

    #         # Render to framebuffer with shader
    #         fbo.clear(0.0, 0.0, 0.0)
    #         texture.use()
    #         vao.render(moderngl.TRIANGLE_STRIP)

    #         # Read pixels from framebuffer
    #         data = fbo.read(components = 3, alignment = 1)

    #         # To numpy array and flip from OpenGL coordinates
    #         image_output = np.flipud(
    #             np.frombuffer(data, dtype = np.uint8).reshape((video.height, video.width, 3))
    #         )
    #         # Turn into a frame
    #         video_frame = av.VideoFrame.from_ndarray(image_output, format = 'rgb24')

    #         # Write
    #         packet = video_writer.stream.encode(video_frame)
    #         if packet:
    #             video_writer.output.mux(packet)

    #         print(f'Frame {str(frame_index)}: {timer.time_elapsed_str}s')

    #         frame_index += 1

    # # Empty codification buffers
    # packet = video_writer.stream.encode(None)
    # if packet:
    #     video_writer.output.mux(packet)

    # # This below is the main workflow with frames
    # # and packets when processing a video
    # do_process_video: bool = False
    # do_process_audio: bool = False
    # for frame_or_packet in video.iterate_with_audio():
    #     if frame_or_packet.is_video_frame:
    #         if do_process_video:
    #             # If we are processing it, we need to decode
    #             frame_decoded = frame_or_packet.decode()
    #         else:
    #             # if we are not processing it, just copy
    #             # video_writer.output.mux(frame_or_packet)
    #             pass
    #     elif frame_or_packet.is_audio_frame:
    #         if do_process_audio:
    #             # If we are processing it, we need to decode
    #             frame_decoded = frame_or_packet.decode()
    #         else:
    #             # if we are not processing it, just copy
    #             # video_writer.output.mux(frame_or_packet)
    #             pass
    #     elif frame_or_packet.is_video_packet:
    #         if do_process_video:
    #             # If we are processing it, we need to decode
    #             # the packet, that will give us an array of
    #             # frames
    #             for frame_decoded in frame_or_packet.decode():
    #                 pass
    #         else:
    #             # If we are not processing it, just copy
    #             # video_writer.output.mux(packet)
    #             pass
    #     elif frame_or_packet.is_audio_packet:
    #         if do_process_audio:
    #             # If we are processing it, we need to decode
    #             # the packet, that will give us an array of
    #             # frames
    #             for frame_decoded in frame_or_packet.decode():
    #                 pass
    #         else:
    #             # If we are not processing it, just copy
    #             # video_writer.output.mux(packet)
    #             pass

    
    for packet in video.frame_with_audio_iterator:
        # The frames don't come in a specific order.
        # In this specific case we receive 1 or 2
        # video frames per each audio frame, but
        # they come always ordered.
        if packet.stream.type == 'video':
            for frame in packet.decode():
                with Timer(is_silent_as_context = True) as timer:
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
                    out_frame = av.VideoFrame.from_ndarray(processed_data, format = NUMPY_FORMAT)
                    # TODO: What is this for (?)
                    #out_frame.pict_type = 'NONE'

                    for v_packet in video_writer.video_stream.encode(out_frame):
                        # Check that the packet received is not the
                        # one that indicates the end (that must not
                        # be passed to the mux)
                        if v_packet.size > 0:
                            video_writer.output.mux(v_packet)

                    frame_index += 1
                print(f'Frame {str(frame_index)}: {timer.time_elapsed_str}s')

        elif packet.stream.type == "audio":
            print('-- AUDIO --')
            # Check that the packet received is not the
            # one that indicates the end (that must not
            # be passed to the mux)
            if packet.size > 0:
                # Copy audio as it is
                video_writer.output.mux(packet)

    # Empty buffers
    # This '.encode()' with no params will tell the
    # encoder that you will not send more packets, 
    # so it can process the remaining ones, that
    # are the ones obtained in the 'packet' var.
    # While this code can be finished, the work in
    # the muxer could be not finished and have some
    # packets waiting to be written. Here we tell
    # the muxer to process all those packets.
    for packet in video_writer.video_stream.encode():
        video_writer.output.mux(packet)

    # TODO: Maybe move this to the '__del__' (?)
    video_writer.output.close()
    video.container.close()
    print(f'Saved as "{OUTPUT_PATH}".')
