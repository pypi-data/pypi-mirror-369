
import dearpygui.dearpygui as dpg
import pyvista as pv
import numpy as np
from pyvistaqt import BackgroundPlotter

# 生成示例点云数据
def generate_point_cloud():
    points = np.random.rand(1000, 3) * 2 - 1
    colors = np.random.rand(1000, 3)
    return pv.PolyData(points), colors

# 主界面
def create_gui():
    dpg.create_context()
    dpg.create_viewport(title='3D Point Cloud Viewer', width=1200, height=800)
    
    with dpg.window(label="Control Panel", width=300, height=800):
        dpg.add_text("Point Cloud Controls")
        dpg.add_slider_int(label="Point Size", default_value=5, min_value=1, max_value=20, callback=update_render)
        dpg.add_color_edit(label="Background", default_value=[0.1, 0.1, 0.1], callback=update_render)
        
    # 嵌入PyVista渲染窗口
    plotter = BackgroundPlotter(window_size=(900, 800))
    cloud, colors = generate_point_cloud()
    plotter.add_mesh(cloud, scalars=colors, rgb=True, point_size=5)
    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    while dpg.is_dearpygui_running():
        plotter.app.process_events()
        dpg.render_dearpygui_frame()
    dpg.destroy_context()

def update_render(sender, app_data):
    pass  # 可添加参数更新逻辑

if __name__ == "__main__":
    create_gui()
