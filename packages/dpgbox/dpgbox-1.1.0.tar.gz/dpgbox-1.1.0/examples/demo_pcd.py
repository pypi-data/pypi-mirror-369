import dearpygui.dearpygui as dpg
import open3d as o3d
import numpy as np
import dpgbox as dpb

# 初始化 Dear PyGui
dpg.create_context()
# dpg.configure_app(docking=True, docking_space=True)

dpb.register_font_theme(tag="themeFontChinese")
dpg.bind_font("themeFontChinese")

# 创建 Open3D 渲染器
def create_o3d_renderer():
    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False)  # 隐藏原生窗口:ml-citation{ref="1" data="citationList"}
    return vis

# 点云处理函数
def process_point_cloud(file_path):
    pcd = o3d.io.read_point_cloud(file_path)  # 加载点云:ml-citation{ref="2,5" data="citationList"}
    pcd = pcd.voxel_down_sample(voxel_size=0.03)  # 降采样:ml-citation{ref="2" data="citationList"}
    pcd.estimate_normals()  # 计算法线:ml-citation{ref="1" data="citationList"}
    return pcd

# 创建纹理注册表
with dpg.texture_registry():
    width, height = 1920, 1080
    texture_id = dpg.add_dynamic_texture(width, height, [])

# 全局变量
vis = create_o3d_renderer()
current_pcd = None

# 加载点云回调
def load_point_cloud(file_path):
    global current_pcd
    try:
        current_pcd = process_point_cloud(file_path)
        vis.clear_geometries()
        vis.add_geometry(current_pcd)
        dpg.set_value("status_text", f"已加载: {file_path.split('/')[-1]}")
    except Exception as e:
        dpg.set_value("status_text", f"错误: {str(e)}")

# 更新点尺寸
def update_point_size(value):
    if current_pcd:
        opt = vis.get_render_option()
        opt.point_size = value  # :ml-citation{ref="1" data="citationList"}

# 更新点颜色
def update_point_color(color):
    if current_pcd:
        # 转换颜色值 (0-255) -> (0.0-1.0)
        color = [c/255.0 for c in color[:3]] 
        current_pcd.paint_uniform_color(color)
        vis.update_geometry(current_pcd)


# 渲染更新函数
def update_render():
    if vis:
        # 捕获 Open3D 渲染帧
        image = vis.capture_screen_float_buffer(do_render=True)
        # img_array = (np.asarray(image)*255)
        img_array = np.asarray(image)
        img_array = img_array / np.max(img_array)
        print(img_array.shape, img_array.dtype)
        # 更新 Dear PyGui 纹理
        dpg.set_value(texture_id, img_array)
        print("====update_render")

# 重置视角
def reset_viewpoint():
    vis.reset_view_point(True)  # :ml-citation{ref="1" data="citationList"}

# 表面重建
def surface_reconstruction():
    if current_pcd:
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
            current_pcd, alpha=0.05
        )  # :ml-citation{ref="3" data="citationList"}
        vis.clear_geometries()
        vis.add_geometry(mesh)
        dpg.set_value("status_text", "表面重建完成")
        update_render()

# 主界面
with dpg.window(label="3D 点云查看器", width=800, height=600):
    dpg.add_image(texture_id, tag="point_cloud_view")
    
    # 控制面板
    with dpg.collapsing_header(label="控制面板"):
        dpg.add_file_dialog(
            directory_selector=False,
            show=False,
            callback=lambda s, d: load_point_cloud(d['file_path_name']),
            tag="file_dialog",
            width=700, height=400
        )
        dpg.add_file_extension(".pcd", parent="file_dialog")
        dpg.add_button(label="加载点云文件", callback=lambda: dpg.show_item("file_dialog"))
        dpg.add_slider_float(
            label="点尺寸", 
            min_value=0.5, 
            max_value=10.0, 
            default_value=3.0,
            callback=lambda s, d: update_point_size(d)
        )
        dpg.add_color_edit(
            label="点云颜色",
            default_value=(128, 128, 128),
            callback=lambda s, d: update_point_color(d)
        )
        dpg.add_button(label="重置视角", callback=reset_viewpoint)
        dpg.add_button(label="表面重建", callback=surface_reconstruction)


# 状态栏
with dpg.window(label="状态栏", width=800, height=30, no_title_bar=True, no_move=True, 
               no_resize=True, pos=(0, 600)):
    dpg.add_text("就绪", tag="status_text")


# 主循环设置
dpg.create_viewport(title='3D点云查看器', width=830, height=650)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
