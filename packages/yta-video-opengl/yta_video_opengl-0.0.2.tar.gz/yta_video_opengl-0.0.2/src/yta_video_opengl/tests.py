"""
Manual tests that are working and are interesting
to learn about the code, refactor and build
classes.
"""
from yta_video_frame_time import T
from PIL import Image

import av
# This 'glfw' is only needed to show in a window
import glfw
import moderngl
import numpy as np
import time

def video_modified_displayed_on_window():
    # -------- CONFIG --------
    VIDEO_PATH = "test_files/test_1.mp4"  # Cambia por tu vídeo
    AMP = 0.05
    FREQ = 10.0
    SPEED = 2.0
    # ------------------------

    # Inicializar ventana GLFW
    if not glfw.init():
        raise RuntimeError("No se pudo inicializar GLFW")

    window = glfw.create_window(1280, 720, "Wave Shader Python", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("No se pudo crear ventana GLFW")

    glfw.make_context_current(window)
    ctx = moderngl.create_context()

    # Shader GLSL
    prog = ctx.program(
        vertex_shader='''
        #version 330
        in vec2 in_pos;
        in vec2 in_uv;
        out vec2 v_uv;
        void main() {
            v_uv = in_uv;
            gl_Position = vec4(in_pos, 0.0, 1.0);
        }
        ''',
        fragment_shader='''
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

    # Cuadrado a pantalla completa
    vertices = np.array([
        -1, -1, 0.0, 0.0,
        1, -1, 1.0, 0.0,
        -1,  1, 0.0, 1.0,
        1,  1, 1.0, 1.0,
    ], dtype='f4')

    vbo = ctx.buffer(vertices.tobytes())
    vao = ctx.simple_vertex_array(prog, vbo, 'in_pos', 'in_uv')

    # Abrir vídeo con PyAV
    container = av.open(VIDEO_PATH)
    stream = container.streams.video[0]
    fps = stream.average_rate
    stream.thread_type = "AUTO"

    # Decodificar primer frame para crear textura
    first_frame = next(container.decode(stream))
    img = first_frame.to_image().transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
    tex = ctx.texture(img.size, 3, img.tobytes())
    tex.build_mipmaps()

    # Uniforms fijos
    prog['amp'].value = AMP
    prog['freq'].value = FREQ
    prog['speed'].value = SPEED

    # Render loop
    frame_index = 0
    start_time = time.time()
    frame_iter = container.decode(stream)
    for frame in frame_iter:
        if glfw.window_should_close(window):
            break

        # Time
        """
        When showing in the window the frames are very
        slow if using the T, thats why I'm using the
        time, but still not very fast... I think it
        depends on my GPU.
        """
        prog['time'].value = time.time() - start_time
        #prog['time'].value = T.video_frame_index_to_video_frame_time(frame_index, float(fps))

        # Convertir frame a textura
        img = frame.to_image().transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
        tex.write(img.tobytes())

        # Dibujar
        ctx.clear(0.1, 0.1, 0.1)
        tex.use()
        vao.render(moderngl.TRIANGLE_STRIP)
        glfw.swap_buffers(window)
        glfw.poll_events()

        frame_index += 1

    glfw.terminate()

def video_modified_stored():
    VIDEO_PATH = "test_files/test_1.mp4"
    OUTPUT_PATH = "test_files/output.mp4"
    AMP = 0.05
    FREQ = 10.0
    SPEED = 2.0

    # Crear contexto ModernGL sin ventana
    ctx = moderngl.create_standalone_context()

    # Shader de onda
    prog = ctx.program(
        vertex_shader='''
        #version 330
        in vec2 in_pos;
        in vec2 in_uv;
        out vec2 v_uv;
        void main() {
            v_uv = in_uv;
            gl_Position = vec4(in_pos, 0.0, 1.0);
        }
        ''',
        fragment_shader='''
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
    ], dtype='f4')
    vbo = ctx.buffer(vertices.tobytes())
    vao = ctx.simple_vertex_array(prog, vbo, 'in_pos', 'in_uv')

    from yta_video_opengl.reader import VideoReader
    from yta_video_opengl.writer import VideoWriter
    video = VideoReader(VIDEO_PATH)

    # Framebuffer para renderizar
    fbo = ctx.simple_framebuffer(video.size)
    fbo.use()

    # Decodificar primer frame y crear textura
    first_frame = video.next_frame

    # This below is with numpy
    # Most of OpenGL textures expect origin in lower
    # left corner
    # TODO: What if alpha (?)
    image = np.flipud(first_frame.to_ndarray(format = "rgb24"))
    tex = ctx.texture((image.shape[1], image.shape[0]), 3, image.tobytes())

    # # This below is with Pillow
    # # TODO: Why not to ndarray? It's faster
    # img = first_frame.to_image().transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
    # tex = ctx.texture(img.size, 3, img.tobytes())

    tex.build_mipmaps()

    # Uniforms
    prog['amp'].value = AMP
    prog['freq'].value = FREQ
    prog['speed'].value = SPEED

    # Abrir salida con PyAV (codificador H.264)
    video_writer = VideoWriter(OUTPUT_PATH, video.fps, video.size, 'yuv420p')
    output_stream = video_writer._stream

    frame_index = 0
    
    for frame in video.frame_iterator:
        prog['time'].value = T.video_frame_index_to_video_frame_time(frame_index, float(video.fps))

        # This below is with numpy
        # To numpy array and flip to OpenGL coordinates
        img_array = np.flipud(
            frame.to_ndarray(format = "rgb24")
        )

        # Subir a textura
        tex = ctx.texture((img_array.shape[1], img_array.shape[0]), 3, img_array.tobytes())

        # This bellow is with Pillow
        # Subir frame a textura
        img = frame.to_image().transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")

        tex.write(img.tobytes())

        # Renderizar con shader al framebuffer
        fbo.clear(0.0, 0.0, 0.0)
        tex.use()
        vao.render(moderngl.TRIANGLE_STRIP)

        # Leer píxeles del framebuffer
        data = fbo.read(components = 3, alignment = 1)

        # To numpy array and flip to OpenGL coordinates
        img_out = np.flipud(
            np.frombuffer(data, dtype = np.uint8).reshape((video.height, video.width, 3))
        )
        # Turn into a frame
        video_frame = av.VideoFrame.from_ndarray(img_out)

        # # This below is with Pillow
        # img_out = Image.frombytes("RGB", video.size, data).transpose(Image.FLIP_TOP_BOTTOM)
        # # Trn into a frame
        # video_frame = av.VideoFrame.from_image(img_out)

        # Write
        packet = output_stream.encode(video_frame)
        if packet:
            video_writer._output.mux(packet)

        frame_index += 1

    # Vaciar buffers de codificación
    packet = output_stream.encode(None)
    if packet:
        video_writer._output.mux(packet)

    video_writer._output.close()
    print(f"Vídeo guardado en {OUTPUT_PATH}")
