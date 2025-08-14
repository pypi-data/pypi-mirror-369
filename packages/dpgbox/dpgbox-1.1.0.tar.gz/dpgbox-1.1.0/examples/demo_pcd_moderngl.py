import dearpygui.dearpygui as dpg
import moderngl
import numpy as np
from PIL import Image

# 初始化 DPG
dpg.create_context()

# 创建窗口
dpg.create_viewport(title='3D Point Cloud with ModernGL', width=800, height=600)
dpg.setup_dearpygui()

# 创建主窗口
with dpg.window(label="Point Cloud Viewer", width=800, height=600) as window_id:
    # 创建一个纹理用于显示 ModernGL 渲染结果
    texture_id = dpg.add_dynamic_texture(800, 600, np.zeros((800, 600, 3), dtype=np.float32), parent=window_id)

# 初始化 ModernGL 上下文
ctx = moderngl.create_context(require=330)  # 需要 OpenGL 3.3
ctx.enable(moderngl.DEPTH_TEST)

# 创建 FBO（帧缓冲对象）
fbo = ctx.simple_framebuffer((800, 600))
fbo.use()

# 生成随机点云数据
num_points = 10000
points = np.random.randn(num_points, 3).astype('f4')  # (x, y, z)
colors = np.random.rand(num_points, 3).astype('f4')   # (r, g, b)

# 创建 VBO 和 VAO
vbo_points = ctx.buffer(points)
vbo_colors = ctx.buffer(colors)
vao = ctx.vertex_array(
    ctx.program(
        vertex_shader='''
            #version 330
            uniform mat4 mvp;
            in vec3 in_position;
            in vec3 in_color;
            out vec3 v_color;
            void main() {
                v_color = in_color;
                gl_Position = mvp * vec4(in_position, 1.0);
                gl_PointSize = 2.0;  // 点的大小
            }
        ''',
        fragment_shader='''
            #version 330
            in vec3 v_color;
            out vec4 f_color;
            void main() {
                f_color = vec4(v_color, 1.0);
            }
        '''
    ),
    [
        (vbo_points, '3f', 'in_position'),
        (vbo_colors, '3f', 'in_color')
    ]
)

# 旋转角度
angle = 0.0

def render_point_cloud():
    global angle

    # 清除 FBO
    fbo.clear(0.0, 0.0, 0.0, 1.0)

    # 构建 MVP 矩阵（模型-视图-投影）
    proj = ctx.matrix44.perspective_projection(45.0, 800 / 600, 0.1, 100.0)
    view = ctx.matrix44.look_at(
        (3, 3, 3),  # 相机位置
        (0, 0, 0),  # 看向原点
        (0, 1, 0)   # 上方向
    )
    model = ctx.matrix44.rotation_x(angle) @ ctx.matrix44.rotation_y(angle)
    mvp = proj @ view @ model

    # 传递 MVP 矩阵给着色器
    vao.program['mvp'].write(mvp.astype('f4').tobytes())

    # 绘制点云
    vao.render(moderngl.POINTS)

    # 将 FBO 内容读取为图像
    fbo_content = np.frombuffer(fbo.read(components=3, dtype='f1'), dtype='uint8')
    fbo_content = fbo_content.reshape(600, 800, 3)
    fbo_content = fbo_content[::-1, :, :]  # 垂直翻转（OpenGL 坐标系）

    # 更新 DPG 纹理
    with dpg.texture_registry():
        dpg.set_value(texture_id, fbo_content.astype(np.float32) / 255.0)

    # 更新旋转角度
    angle += 0.01

# 在 DPG 渲染循环中调用 ModernGL 渲染
with dpg.handler_registry():
    dpg.add_frame_callback(callback=lambda: render_point_cloud())

# 显示图像
with dpg.window(label="Render", width=800, height=600):
    dpg.add_image(texture_id)

# 启动 DPG
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()